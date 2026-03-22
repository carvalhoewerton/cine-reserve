import os
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_ticket_email(user_email, user_name, tickets_data):
    seats = ', '.join([ticket['seat_label'] for ticket in tickets_data])
    movie = tickets_data[0]['movie_name']
    session = tickets_data[0]['session_starts_at']
    room = tickets_data[0]['room_name']

    send_mail(
        subject='Sua reserva foi feita!',
        message=f'''
            Caro(a) {user_name},
            
            Sua reserva foi confirmada com sucesso!
            
            Filme: {movie}
            Sessão: {session}
            Sala: {room}
            Assentos: {seats}
            
            Bom filme!
            Cinépolis Natal
                    ''',
        from_email=os.getenv('EMAIL_HOST_USER'),
        recipient_list=[user_email],
    )