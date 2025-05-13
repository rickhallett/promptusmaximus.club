'use client'; // Required for useState and event handlers

import Image from 'next/image';
import { useState, FormEvent } from 'react';

export default function Home() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setMessage('');

    // Client-side validation (simple presence check, browser does type check)
    if (!email) {
      setMessage('Please enter your email address.');
      setIsLoading(false);
      return;
    }

    // Honeypot field is part of the form, name="honeypot-email"
    const formData = new FormData(event.currentTarget);
    // No need to explicitly get honeypot value here for client-side check, 
    // server will handle it. It being in formData is enough.

    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        body: formData, // Send FormData directly
      });

      if (response.ok) {
        // Successful redirect is handled by the browser if action/method were used.
        // If fetch is used and API returns redirect, window.location can be used.
        // Here, assuming API returns 302, and we might want to manually redirect or show success.
        if (response.redirected) {
          window.location.href = response.url; // Follow server-side redirect
        } else {
          // Should not happen if API correctly redirects, but handle as success
          setMessage('Subscription successful! Redirecting...');
          // Optionally, redirect after a delay or based on a specific success message
          // For now, we assume server handles redirect to /thanks for fetch too
          // or that the form action/method handles it if JS is disabled.
          // If API sends JSON for success (not a redirect), handle here:
          // const result = await response.json(); 
          // setMessage(result.message || 'Success!');
          // setEmail(''); // Clear email field
        }
      } else {
        const errorData = await response.json();
        setMessage(errorData.error || 'Submission failed. Please try again.');
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setMessage('An error occurred. Please try again later.');
    }
    setIsLoading(false);
  };

  return (
    <div className="bg-stone-900 text-amber-50 min-h-screen flex flex-col items-center">
      <header className="w-full p-4 flex justify-between items-center max-w-6xl mx-auto">
        <div className="text-2xl font-bold">Promptus Maximus</div>
        <nav className="space-x-4">
          <a href="#codex" className="hover:text-amber-400">Codex</a>
          <a href="#cohort" className="hover:text-amber-400">Arena Cohort</a>
          <a href="#login" className="hover:text-amber-400">Login</a>
        </nav>
      </header>
      <main className="flex flex-col items-center justify-center flex-grow w-full px-4">
        <section id="hero" className="w-full max-w-4xl text-center py-16 md:py-24">
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-amber-500">Join the Legion:</h1>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-amber-500">Promptus Maximus</h1>
          <h2 className="mt-6 text-lg md:text-xl max-w-prose mx-auto opacity-80">Forge unbreakable prompts, wield stoic strategy, and spar with the world's most advanced LLMs —no prior code or toga exp required.</h2>
          <p className="mt-4 italic text-md opacity-70">Your Campus, Our Colosseum, One Distributed Language Model (DLM).</p>

          <div className="mt-10 flex justify-center">
            <Image
              src="/hero.png"
              alt="Promptus Maximus"
              width={300}
              height={300}
            />
          </div>

          <form onSubmit={handleSubmit} className="mt-10">
            {/* Honeypot field for spam prevention */}
            <div className="absolute left-[-5000px]" aria-hidden="true">
              <label htmlFor="honeypot-email" className="sr-only">Don\'t fill this out if you\'re human:</label>
              <input type="text" id="honeypot-email" name="honeypot-email" tabIndex={-1} autoComplete="off" />
            </div>

            <div id="cta-block" className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <input
                type="email"
                name="email"
                placeholder="your@uni.edu"
                required
                value={email} // Controlled component
                onChange={(e) => setEmail(e.target.value)}
                className="w-full md:w-64 px-4 py-3 rounded-lg bg-stone-800 border border-stone-700 text-amber-50 focus:ring-amber-500 focus:border-amber-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                className="bg-amber-600 hover:bg-rose-600 text-stone-900 font-semibold px-6 py-3 rounded-lg w-full sm:w-auto disabled:opacity-50"
                disabled={isLoading}
              >
                {isLoading ? 'Unlocking...' : 'Unlock the Codex'}
              </button>
            </div>
            {message && <p className={`mt-4 text-sm ${message.includes('failed') || message.includes('error') || message.includes('Please enter') ? 'text-red-400' : 'text-green-400'}`}>{message}</p>}
            <p className="mt-4 text-sm opacity-60">Join 297 fellow prompt gladiators.</p>
          </form>
        </section>

        <section id="features" className="w-full max-w-5xl py-16 md:py-24">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-amber-500 mb-12">What You Will Master</h2>
          <div className="flex flex-col gap-8 md:grid md:grid-cols-2 lg:grid-cols-3">
            {[
              "Gladiator-grade Prompt Craft — tone, structure, few-shot wizardry.",
              "Context Alchemy — fuse your background with the model\'s bias for sharper output.",
              "Stoic Mindset Drills — resilience, clarity, and ethical guard-rails from the Meditations.",
              "Hands-on AI Sparring Matches — real-time critique sessions with ≥ GPT-3o-class models.",
              "Think Like a Programmer — critical, Socratic, inductive & deductive reasoning patterns.",
              "Hyper-Intelligence Protocol — become noticeably smarter in less screen-time.",
              "10× Input Clarity → 10× Output Impact — compound leverage through prompt design.",
              "Lifetime Access to the Promptus Maximus Codex — version-controlled prompt library."
            ].map((feature, index) => (
              <div key={index} className="bg-stone-800 p-6 rounded-lg shadow-lg border border-stone-700">
                <h3 className="text-xl font-semibold text-amber-500 mb-2">{feature.split(" — ")[0]}</h3>
                <p className="text-amber-50 opacity-80">{feature.split(" — ")[1] || ""}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="cohort-banner" className="w-full bg-stone-950 py-8 my-16 md:my-24 border-y-2 border-amber-500">
          <div className="max-w-4xl mx-auto text-center px-4">
            <h3 className="text-2xl md:text-3xl font-semibold text-amber-400">Promptus Maximus Pro: Arena Cohort ∙ Summer 2025</h3>
            <p className="mt-2 text-lg text-amber-100 opacity-90">Limited seats · first come, first served.</p>
          </div>
        </section>

        <section id="social-proof" className="w-full max-w-5xl py-16 md:py-24 px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-amber-500 mb-12">Wisdom from the Arena</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[{
              quote: "I used the sparring sessions to prep for tech-interview case studies—walked in with bullet-proof reasoning paths.",
              attribution: "Miguel R., junior software-engineer hire"
            }, {
              quote: "I\'m not a coder, but the Stoic mindset drills kept me from rage-quitting when GPT spat out garbage. Now I iterate instead of panic.",
              attribution: "Emily S., journalism major"
            }, {
              quote: "Weekly product-update emails went from two hours to twenty minutes. My manager asked what template I\'d stolen.",
              attribution: "Jason L., SaaS product manager"
            }, {
              quote: "I had no idea what \'few-shot\' meant. One lesson later, my language-learning flashcards feel like a personal tutor.",
              attribution: "Hana O., linguistics undergrad"
            }, {
              quote: "The cohort\'s live critique turned my half-baked startup pitch into a clear, data-backed story. Landed a seed-round meeting.",
              attribution: "Ben T., first-time founder"
            }].map((testimonial, index) => (
              <figure key={index} className="bg-stone-800 p-6 rounded-lg shadow-lg border border-stone-700 flex flex-col">
                <blockquote className="text-amber-50 opacity-90 italic mb-4 flex-grow">
                  <p>{`“${testimonial.quote}”`}</p>
                </blockquote>
                <figcaption className="text-amber-400 font-semibold text-sm text-right">
                  — {testimonial.attribution}
                </figcaption>
              </figure>
            ))}
          </div>
        </section>

      </main>
      <footer className="w-full p-8 text-center border-t border-stone-800 mt-16 md:mt-24">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-lg font-semibold">Promptus Maximus</div>
          <div className="space-x-6">
            <a href="#terms" className="hover:text-amber-400 text-sm">Terms</a>
            <a href="#privacy" className="hover:text-amber-400 text-sm">Privacy</a>
            <a href="#contact" className="hover:text-amber-400 text-sm">Contact</a>
          </div>
          <p className="text-sm opacity-70 mt-4 md:mt-0">© 2024 Promptus Maximus. All rights reserved.</p>
        </div>
        <p className="mt-8 text-xs opacity-50">Built with stoic calm and silicon fire.</p>
      </footer>
    </div>
  );
}
