import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';

// Initialize Resend with API Key (ensure this is set in your environment variables)
const resendApiKey = process.env.RESEND_API_KEY;
const resend = resendApiKey ? new Resend(resendApiKey) : null;
const contactListId = process.env.RESEND_CONTACT_LIST_ID; // Or your specific audience/list ID

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const email = formData.get('email') as string;
    const honeypotEmail = formData.get('honeypot-email') as string;

    // 1. Honeypot validation
    if (honeypotEmail) {
      console.log('Honeypot field filled, likely spam.');
      // Silently succeed or redirect to a generic page to not alert the bot
      return NextResponse.redirect(new URL('/thanks', request.url), 302);
    }

    // 2. Email validation (basic)
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      return NextResponse.json({ error: 'Invalid email address' }, { status: 400 });
    }

    // 3. Add to Resend contact list
    if (!resend) {
      console.error('Resend client not initialized. RESEND_API_KEY missing or invalid.');
      return NextResponse.json({ error: 'Email service configuration error.' }, { status: 500 });
    }
    if (!contactListId) {
      console.error('RESEND_CONTACT_LIST_ID not set.');
      return NextResponse.json({ error: 'Email service configuration error (missing list ID).' }, { status: 500 });
    }

    try {
      const { data, error } = await resend.contacts.create({
        email: email,
        audienceId: contactListId,
      });

      if (error) {
        console.error('Resend API error:', error);
        const errorMessage = (error as Error).message || 'Unknown Resend API error';
        return NextResponse.json({ error: 'Failed to subscribe email.', details: errorMessage }, { status: 500 });
      }

      console.log('Successfully subscribed email:', email, 'Data:', data);
      return NextResponse.redirect(new URL('/thanks', request.url), 302);

    } catch (resendError: unknown) {
      console.error('Error during Resend operation:', resendError);
      const errorMessage = resendError instanceof Error ? resendError.message : 'An unexpected error occurred with the email service.';
      return NextResponse.json({ error: 'An unexpected error occurred with the email service.', details: errorMessage }, { status: 500 });
    }

  } catch (error: unknown) {
    console.error('Error processing subscription request:', error);
    const errorMessage = error instanceof Error ? error.message : 'Invalid request';
    return NextResponse.json({ error: 'Invalid request', details: errorMessage }, { status: 400 });
  }
}
