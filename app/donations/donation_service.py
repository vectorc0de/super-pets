from flask import jsonify, session, current_app, request
import stripe
from datetime import datetime, timedelta
import uuid
from app.models.people_model import PeopleModel
from app.email_utils import (
    send_payment_confirmation_email,
    generate_invoice_html,
    send_invoice_email_via_resend
)

def get_client_id():
    client_id = session.get('user_id')
    if not client_id:
        return None, jsonify({"success": False, "error": "Client not logged in"}), 401
    return client_id, None, None

def process_credit_donation(donation_id, payment_method_id):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    try:
        donation_response = current_app.supabase.table('donations').select('*').eq('donation_id', donation_id).single().execute()

        if not donation_response.data:
            return jsonify({'error': 'Donation not found'}), 404

        donation = donation_response.data
        amount = donation['amount']
        currency = donation['currency']
        title = donation.get('title', 'Donation')
        description = donation.get('description', '')
        to_email = donation.get('email')

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method_id,
            confirmation_method="manual",
            confirm=True,
            description=f"{title}: {description}",
            return_url="https://your-website.com/payment-complete"
        )

        if payment_intent.status == "requires_action":
            return jsonify({
                'requires_action': True,
                'payment_intent_client_secret': payment_intent.client_secret,
                'return_url': payment_intent.next_action.redirect_to_url.url
            }), 200
        elif payment_intent.status == "succeeded":
            current_app.supabase.table('donations').update({
                'payment_method_id': payment_method_id,
                'payment_status': 'Succeeded',
                'stripe_payment_intent_id': payment_intent.id
            }).eq('donation_id', donation_id).execute()

            first_name = donation.get('first_name', '')
            send_payment_confirmation_email(to_email, first_name, amount, title)

            return jsonify({
                'success': True,
                'message': 'Donation payment successful',
                'donation_id': donation_id
            }), 200
        else:
            return jsonify({'error': 'Payment failed'}), 400

    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred during the donation process {e}'}), 500

def process_credit_donation_auto(data):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    try:
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        title = data.get('title', 'Donation')
        description = data.get('description', '')
        payment_method_id = data.get('payment_method_id')
        to_email = data.get('email')

        if not amount or not payment_method_id or not to_email:
            return jsonify({'error': 'Required fields are missing: amount, payment_method_id, email'}), 400

        donation_id = str(uuid.uuid4())
        current_app.supabase.table('donations').insert({
            'donation_id': donation_id,
            'client_id': client_id,
            'amount': amount,
            'currency': currency,
            'title': title,
            'description': description,
            'payment_method_id': 'Pending',
            'payment_status': 'Pending',
            'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'email': to_email,
        }).execute()

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method_id,
            confirmation_method="manual",
            confirm=True,
            description=f"{title}: {description}",
            return_url="https://your-website.com/payment-complete"
        )

        if payment_intent.status == "requires_action":
            return jsonify({
                'requires_action': True,
                'payment_intent_client_secret': payment_intent.client_secret,
                'return_url': payment_intent.next_action.redirect_to_url.url
            }), 200
        elif payment_intent.status == "succeeded":
            current_app.supabase.table('donations').update({
                'payment_method_id': payment_method_id,
                'payment_status': 'Succeeded',
                'stripe_payment_intent_id': payment_intent.id
            }).eq('donation_id', donation_id).execute()

            first_name = data.get('first_name', '')
            send_payment_confirmation_email(to_email, first_name, amount, title)

            return jsonify({
                'success': True,
                'message': 'Donation payment successful',
                'donation_id': donation_id
            }), 200
        else:
            return jsonify({'error': 'Payment failed'}), 400

    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred during the donation process: {e}'}), 500


def get_all_donations():
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    try:
        response = current_app.supabase.table('donations').select('*').eq('client_id', client_id).in_('payment_status', ['Pending', 'Succeeded']).execute()

        if response.data:
            donations = response.data

            pending_donations = [donation for donation in donations if donation['payment_status'] == 'Pending']
            successful_donations = [donation for donation in donations if donation['payment_status'] == 'Succeeded']

            pending_count = len(pending_donations)
            successful_count = len(successful_donations)
            pending_total_amount = sum(float(donation['amount']) for donation in pending_donations)
            successful_total_amount = sum(float(donation['amount']) for donation in successful_donations)

            return jsonify({
                'success': True,
                'data': donations,
                'summary': {
                    'pending': {
                        'count': pending_count,
                        'total_amount': pending_total_amount
                    },
                    'successful': {
                        'count': successful_count,
                        'total_amount': successful_total_amount
                    }
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'No pending or successful donations found for this client.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred while fetching donations: {str(e)}'}), 500


def create_invoice(data):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code
    
    people_model = PeopleModel(current_app.supabase)
    customer_id = data.get('customer_id')
    amount = data.get('amount')
    title = data.get('title')
    description = data.get('description')

    if not customer_id or not amount or not title or not description:
        return jsonify({'success': False, 'message': 'Required fields are missing'}), 400

    try:
        person_details_response = people_model.get_person_by_id(customer_id)
        if not person_details_response['success']:
            return jsonify({'success': False, 'message': 'Failed to retrieve person details'}), 400

        email = person_details_response['data'].get('person_email')
        phone = person_details_response['data'].get('person_phone')
        address = person_details_response['data'].get('person_address')
        zipcode = person_details_response['data'].get('person_zipcode')
        city = person_details_response['data'].get('person_city')
        state = person_details_response['data'].get('person_state')

        if not email or not phone:
            return jsonify({'success': False, 'message': 'Email or phone number is missing for this person'}), 400

        donation_id = str(uuid.uuid4())
        response = current_app.supabase.table('donations').insert({
            'donation_id': donation_id,
            'person_id': customer_id,
            'client_id': client_id,
            'amount': amount,
            'currency': 'usd',
            'title': title,
            'description': description,
            'payment_method_id': 'Pending',
            'payment_status': 'Pending',
            'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'email': email,
            'phone_number': phone,
            'address': address,
            'zipcode': zipcode,
            'city': city,
            'state': state
        }).execute()

        if not response.data:
            return jsonify({'success': False, 'message': 'Failed to create donation entry'}), 500

        confirmation_url = f"https://127.0.0.1:3000/invoice/{donation_id}"
        html_content = generate_invoice_html(title, amount, confirmation_url)

        email_status = send_invoice_email_via_resend(email, f"Your {title} Invoice from Paw Portal", html_content)

        if not email_status:
            current_app.logger.error(f"Failed to send invoice email to {email} for donation ID {donation_id}")

        return jsonify({'success': True, 'invoice_id': donation_id}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def process_cash_donation(data):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    people_model = PeopleModel(current_app.supabase)
    person_id = data.get('person_id')
    amount = data.get('amount')
    title = data.get('title')
    description = data.get('description')

    if not person_id or not amount or not title or not description:
        return jsonify({'success': False, 'message': 'Required fields are missing'}), 400

    try:
        person_details_response = people_model.get_person_by_id(person_id)
        if not person_details_response['success']:
            return jsonify({'success': False, 'message': 'Failed to retrieve person details'}), 400

        email = person_details_response['data'].get('person_email')
        phone = person_details_response['data'].get('person_phone')
        address = person_details_response['data'].get('person_address')
        zipcode = person_details_response['data'].get('person_zipcode')
        city = person_details_response['data'].get('person_city')
        state = person_details_response['data'].get('person_state')

        donation_id = str(uuid.uuid4())
        response = current_app.supabase.table('donations').insert({
            'donation_id': donation_id,
            'person_id': person_id,
            'client_id': client_id,
            'amount': amount,
            'currency': 'usd',
            'title': title,
            'description': description,
            'payment_method_id': 'Cash',
            'payment_status': 'Succeeded',
            'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
            'email': email,
            'phone_number': phone,
            'address': address,
            'zipcode': zipcode,
            'city': city,
            'state': state
        }).execute()

        if not response.data:
            return jsonify({'success': False, 'message': 'Failed to record cash donation'}), 500

        return jsonify({
            'success': True,
            'message': 'Cash donation recorded successfully',
            'donation_id': donation_id
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def get_donation_analytics():
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    try:
        span = request.args.get('span', 'd').lower()
        today = datetime.utcnow().date()
        
        if span == 'd':
            start_date = today
        elif span == 'w':
            start_date = today - timedelta(days=today.weekday())
        elif span == 'm':
            start_date = today.replace(day=1)
        elif span == 'y':
            start_date = today.replace(month=1, day=1)
        else:
            return jsonify({'success': False, 'message': 'Invalid span parameter. Use "d", "w", "m", or "y"'}), 400

        supabase_client = current_app.supabase
        donations_response = supabase_client.table('donations').select('*').eq('client_id', client_id).gte('created_at', start_date.isoformat()).execute()

        donations = donations_response.data
        if not donations:
            return jsonify({'success': False, 'message': 'No donations found for the specified period'}), 404

        def safe_convert_to_int(value):
            try:
                return int(value) if value is not None else 0
            except (ValueError, TypeError):
                return 0

        total_amount = sum(safe_convert_to_int(donation['amount']) for donation in donations)
        unique_donors = len(set(donation['person_id'] for donation in donations))

        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        previous_month_response = supabase_client.table('donations').select('amount').eq('client_id', client_id).gte('created_at', first_day_of_previous_month.isoformat()).lte('created_at', last_day_of_previous_month.isoformat()).execute()
        previous_month_donations = previous_month_response.data
        previous_total = sum(safe_convert_to_int(donation['amount']) for donation in previous_month_donations)

        percentage_change = ((total_amount - previous_total) / previous_total * 100) if previous_total else 0

        donations_results = [{
            'donation_id': donation['donation_id'],
            'amount': safe_convert_to_int(donation['amount']),
            'donor_name': f"{donation.get('first_name', '')} {donation.get('last_name', '')}".strip(),
            'payment_status': donation.get('payment_status', 'Unknown'),
            'title': donation.get('title', 'No Title'),
            'description': donation.get('description', 'No Description'),
            'created_at': donation['created_at']
        } for donation in donations]

        return jsonify({
            'success': True,
            'analytics': {
                'total_amount': total_amount,
                'unique_donors': unique_donors,
                'percentage_change': percentage_change,
            },
            'donations': donations_results
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred while fetching donation analytics: {str(e)}'}), 500



def delete_donation(donation_id):
    client_id, error_response, status_code = get_client_id()
    if error_response:
        return error_response, status_code

    try:
        response = current_app.supabase.table('donations').delete().eq('donation_id', str(donation_id)).eq('client_id', client_id).execute()

        if response.data:
            return jsonify({'success': True, 'message': 'Donation deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Donation not found or not authorized to delete this donation.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while deleting the donation.'}), 500


def update_donation(donation_id, data):
    try:
        update_data = {}
        if 'amount' in data:
            update_data['amount'] = data['amount']
        if 'currency' in data:
            update_data['currency'] = data['currency']
        if 'billing_details' in data:
            billing_details = data['billing_details']
            if 'email' in billing_details:
                update_data['email'] = billing_details['email']
            if 'phone' in billing_details:
                update_data['phone_number'] = billing_details['phone']
            if 'name' in billing_details:
                name_parts = billing_details['name'].split(' ', 1)
                update_data['first_name'] = name_parts[0]
                update_data['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            if 'address' in billing_details:
                update_data['address'] = billing_details['address'].get('line1')
                update_data['zipcode'] = billing_details['address'].get('postal_code')
                update_data['city'] = billing_details['address'].get('city')
                update_data['state'] = billing_details['address'].get('state')

        response = current_app.supabase.table('donations').update(update_data).eq('donation_id', str(donation_id)).execute()

        if response.data:
            return jsonify({"success": True, "message": "Donation updated successfully", "data": response.data}), 200
        else:
            return jsonify({"success": False, "error": "Failed to update donation."}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': 'An error occurred while updating the donation.'}), 500

def get_donation_info(donation_id):
    try:
        donation_response = current_app.supabase.table('donations').select('*').eq('donation_id', donation_id).single().execute()

        if not donation_response.data:
            return jsonify({'success': False, 'message': 'Donation not found'}), 404

        donation = donation_response.data

        return jsonify({
            'success': True,
            'donation': {
                'donation_id': donation['donation_id'],
                'amount': donation['amount'],
                'currency': donation['currency'],
                'title': donation.get('title', 'Donation'),
                'description': donation.get('description', ''),
                'email': donation.get('email'),
                'payment_status': donation.get('payment_status', 'Unknown'),
                'created_at': donation['created_at']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500