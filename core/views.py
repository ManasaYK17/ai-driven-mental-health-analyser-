from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import AppointmentForm, WellnessTaskForm
from .models import AssessmentQuestion, Appointment, Counselor, PeerSupport, WellnessTask, TemplateWellnessTask, AppointmentSlot

from django.contrib.auth.models import User
from datetime import datetime, date
from .gemini_utils import get_gemini_response
from .twilio_utils import send_whatsapp_message
from .zoom_utils import create_zoom_meeting

def is_admin(user):
    return user.is_superuser

def home(request):
    return render(request, 'core/home.html')


@login_required
def chatbot(request):
    ai_response = None
    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        if user_message:
            ai_response = get_gemini_response(user_message, role='assistant')
    return render(request, 'core/chatbot.html', {'ai_response': ai_response})


# New: Step-by-step assessment, one question at a time

@login_required
def assessment(request):
    # Get all questions (PHQ-9 + GAD-7) in order
    questions = list(AssessmentQuestion.objects.order_by('category', 'id'))
    total_questions = len(questions)
    # Use session to track progress
    if 'assessment_answers' not in request.session:
        request.session['assessment_answers'] = []
        request.session['assessment_index'] = 0
        request.session['assessment_intro'] = True

    answers = request.session['assessment_answers']
    index = request.session['assessment_index']
    show_intro = request.session.get('assessment_intro', True)

    if request.method == 'POST':
        if show_intro:
            # User pressed start after seeing intro
            request.session['assessment_intro'] = False
            show_intro = False
        else:
            answer = request.POST.get('answer')
            if answer is not None and answer.isdigit():
                answers.append(int(answer))
                index += 1
                request.session['assessment_answers'] = answers
                request.session['assessment_index'] = index

    if not show_intro and index >= total_questions:
        # All questions answered, analyze
        phq9_score = sum(answers[:9]) if len(answers) >= 9 else 0
        gad7_score = sum(answers[9:16]) if len(answers) >= 16 else 0
        # AI analysis
        prompt = f"A student completed a mental health assessment. PHQ-9 score: {phq9_score}, GAD-7 score: {gad7_score}. Give a brief, supportive analysis and next steps."
    ai_response = get_gemini_response(prompt, role='mental health assistant')
        # Clear session
        del request.session['assessment_answers']
        del request.session['assessment_index']
        del request.session['assessment_intro']
        return render(request, 'core/assessment_result.html', {'phq9_score': phq9_score, 'gad7_score': gad7_score, 'ai_response': ai_response})

    ai_chat_response = None

    # Always show intro before first question
    if show_intro or (index == 0 and request.method != 'POST'):
        request.session['assessment_intro'] = True
        if request.method == 'POST':
            # User pressed start after seeing intro
            request.session['assessment_intro'] = False
            return redirect('assessment')
        return render(request, 'core/assessment_intro.html')

    question = questions[index] if index < total_questions else None

    if request.method == 'POST':
        user_message = request.POST.get('ai_chat_message')
        if user_message:
            # If the user types a number (0-3), treat as answer
            if user_message.strip() in ['0', '1', '2', '3']:
                answers.append(int(user_message.strip()))
                index += 1
                request.session['assessment_answers'] = answers
                request.session['assessment_index'] = index
                # Move to next question
                if index < total_questions:
                    question = questions[index]
                else:
                    question = None
            else:
                # Otherwise, treat as AI chat
                prompt = f"A student is taking a mental health assessment. The current question is: '{question.text}'. The student asks: '{user_message}'. Please answer as a supportive mental health assistant."
                ai_chat_response = get_gemini_response(prompt, role='mental health assistant')

    if index >= total_questions:
        # All questions answered, analyze
        phq9_score = sum(answers[:9]) if len(answers) >= 9 else 0
        gad7_score = sum(answers[9:16]) if len(answers) >= 16 else 0
        # AI analysis
        prompt = f"A student completed a mental health assessment. PHQ-9 score: {phq9_score}, GAD-7 score: {gad7_score}. Give a brief, supportive analysis and next steps."
    ai_response = get_gemini_response(prompt, role='mental health assistant')
        # Clear session
        del request.session['assessment_answers']
        del request.session['assessment_index']
        del request.session['assessment_intro']
        return render(request, 'core/assessment_result.html', {'phq9_score': phq9_score, 'gad7_score': gad7_score, 'ai_response': ai_response})

    return render(request, 'core/assessment_step.html', {
        'question': question,
        'index': index+1,
        'total': total_questions,
        'ai_chat_response': ai_chat_response
    })

@login_required
def assessment_result(request):
    # Placeholder: implement score analysis and AI logic
    return render(request, 'core/assessment_result.html')

@login_required
def peer_support(request):
    # Placeholder: implement peer support chat logic
    return render(request, 'core/peer_support.html')

@login_required
def future_you(request):
    ai_response = None
    if request.method == 'POST':
        user_message = request.POST.get('user_message')
        if user_message:
            prompt = f"You are the user, but 10 years older. Motivate and respond as their future self. User says: {user_message}"
        ai_response = get_gemini_response(prompt, role='future self')
    return render(request, 'core/future_you.html', {'ai_response': ai_response})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'core/appointment_list.html', {'appointments': appointments})


@login_required
def book_appointment(request):
    user = request.user
    # Find the next available slot (not booked, soonest)
    slot = AppointmentSlot.objects.filter(is_booked=False).order_by('slot_time').first()
    if not slot:
        return render(request, 'core/book_appointment.html', {'form': None, 'error': 'No available slots. Please try again later.'})

    if request.method == 'POST':
        # Mark slot as booked
        slot.is_booked = True
        slot.save()
        # Create Appointment
        appointment = Appointment.objects.create(
            user=user,
            counselor=slot.counselor,
            date=slot.slot_time,
            status='Confirmed'
        )
        # Send WhatsApp to counselor
        counselor = slot.counselor
        message = f"You have a new booking with {user.username} on {slot.slot_time.strftime('%Y-%m-%d %H:%M')}."
        send_whatsapp_message(counselor.contact, message)
        # Create Zoom meeting
        zoom_url, zoom_err = create_zoom_meeting(
            topic=f"Counseling Session: {user.username}",
            start_time=slot.slot_time,
            duration=30
        )
        # Optionally, send Zoom link to both counselor and user (WhatsApp/email)
        if zoom_url:
            send_whatsapp_message(counselor.contact, f"Zoom meeting link: {zoom_url}")
            if hasattr(user, 'profile') and getattr(user.profile, 'phone', None):
                send_whatsapp_message(user.profile.phone, f"Your counseling session Zoom link: {zoom_url}")
        return redirect('appointment_list')

    # Show slot info for confirmation
    return render(request, 'core/book_appointment.html', {'form': None, 'slot': slot})

@login_required
def profile(request):
    tasks = WellnessTask.objects.filter(assigned_to=request.user)
    return render(request, 'core/profile.html', {'tasks': tasks})

@login_required
def wellness_activity(request):
    user = request.user
    today = date.today()
    # Count how many tasks have already been assigned to this user
    assigned_count = WellnessTask.objects.filter(assigned_to=user).count()
    # Get the next template task (if any)
    next_template = TemplateWellnessTask.objects.order_by('order')[assigned_count:assigned_count+1].first()
    if next_template:
        # Check if today's task is already assigned
        already_assigned = WellnessTask.objects.filter(assigned_to=user, date=today, task=next_template.task).exists()
        if not already_assigned:
            WellnessTask.objects.create(
                task=next_template.task,
                assigned_by=None,
                assigned_to=user,
                date=today,
                completed=False
            )
    # Only show today's task
    todays_task = WellnessTask.objects.filter(assigned_to=user, date=today).first()
    return render(request, 'core/wellness_activity.html', {'todays_task': todays_task})

@login_required
def mark_task_completed(request, task_id):
    task = WellnessTask.objects.get(id=task_id, assigned_to=request.user)
    task.completed = True
    task.save()
    return redirect('wellness_activity')

@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'core/admin_panel.html')

@user_passes_test(is_admin)
def add_counselor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        hospital = request.POST.get('hospital')
        contact = request.POST.get('contact')
        Counselor.objects.create(name=name, location=location, hospital=hospital, contact=contact)
        return redirect('admin_panel')
    return render(request, 'core/add_counselor.html')

@user_passes_test(is_admin)
def add_question(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        category = request.POST.get('category')
        AssessmentQuestion.objects.create(text=text, category=category)
        return redirect('admin_panel')
    return render(request, 'core/add_question.html')

@user_passes_test(is_admin)
def add_task(request):
    if request.method == 'POST':
        task = request.POST.get('task')
        assigned_to_id = request.POST.get('assigned_to')
        date_str = request.POST.get('date')
        assigned_to = User.objects.get(id=assigned_to_id)
        WellnessTask.objects.create(task=task, assigned_to=assigned_to, date=date_str)
        return redirect('admin_panel')
    users = User.objects.filter(is_superuser=False)
    return render(request, 'core/add_task.html', {'users': users})
