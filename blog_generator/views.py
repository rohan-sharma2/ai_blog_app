from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from huggingface_hub import InferenceClient
import json
import yt_dlp as youtube_dl
import os
import assemblyai as aai
import requests
from .models import BlogPost

# Define the path to ffmpeg
FFMPEG_LOCATION = '/usr/bin/ffmpeg'

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)
        
        # Get YouTube title
        title = yt_title(yt_link)

        # Get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)

        # Use Hugging Face to generate the blog
        blog_content = generate_blog_from_transcription(title, transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)

        # Save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # Return blog article as a response
        return JsonResponse({'content': blog_content})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        title = info_dict.get('title', None)
    return title

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': FFMPEG_LOCATION,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    return file_name

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "aai"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def generate_blog_from_transcription(title, transcription):
    client = InferenceClient(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        token="hf_token",
    )

    max_tokens = 8192
    max_new_tokens = 800
    max_input_tokens = max_tokens - max_new_tokens - 1000

    # Function to trim the transcription to fit within the allowed token limit
    def trim_transcription(transcription, max_length):
        words = transcription.split()
        trimmed_words = words[:max_length]
        return ' '.join(trimmed_words)

    # Estimate the length of the transcription in tokens (assuming 1 token ~ 1 word for simplicity)
    transcription_length = len(transcription.split())

    # Trim the transcription if necessary
    if transcription_length > max_input_tokens:
        transcription = trim_transcription(transcription, max_input_tokens)

    prompt = (
        f"Based on the following transcript from a YouTube video, write a comprehensive summarised blog article.\n"
        f"Write it based on the transcript:\n\n"
        f"{transcription}\n\n"
        f"Provide an HTML response with a section-wise bullet-point summarised blog article based on the above transcription. "
        f"Also, add the title of the video at the start as a bold header: <h1><b><u>{title}</u></b></h1>. "
        f"Please avoid repeating phrases or sentences and ensure the content is clear and concise.\n\n"
        f"Use <p> tags for paragraphs, and use section headings with <b> and <h2> tags, like this: <h2><b>Section Title</b></h2>. "
        f"Bullet points should be in <li> format. "
        f"Do not use ** for bold; instead, use <b> and add breaks for new lines.\n\n"
    )

    response = client.text_generation(prompt, max_new_tokens=max_new_tokens)

    if response:
        generated_content = response
    else:
        generated_content = "Failed to generate content."

    def remove_repetitions(text):
        sentences = text.split('. ')
        unique_sentences = []
        for sentence in sentences:
            if sentence not in unique_sentences:
                unique_sentences.append(sentence)
        return '. '.join(unique_sentences) + ('.' if text.endswith('.') else '')

    # Apply the function to the generated content
    cleaned_content = remove_repetitions(generated_content)

    return cleaned_content


def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message': error_message})
        
        else:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')
