import Link from 'next/link';

export default function ThanksPage() {
  return (
    <div className="bg-stone-900 text-amber-50 min-h-screen flex flex-col items-center justify-center px-4">
      <main className="max-w-2xl w-full text-center p-8 bg-stone-800 rounded-lg shadow-2xl border border-stone-700">
        <h1 className="text-3xl md:text-4xl font-bold text-amber-500 mb-6">
          Your Wisdom Seeker&apos;s Oath is Recorded!
        </h1>
        <p className="text-lg opacity-90 mb-4">
          Thank you for joining the ranks of Promptus Maximus.
        </p>
        <blockquote className="my-8 border-l-4 border-amber-600 pl-4 italic">
          <p className="text-xl text-amber-100 opacity-95">
            “The impediment to action advances action. What stands in the way becomes the way.”
          </p>
          <cite className="block mt-2 text-sm text-amber-400 opacity-80">
            — Marcus Aurelius, Meditations
          </cite>
        </blockquote>
        <p className="text-md opacity-80 mb-8">
          The path to prompt mastery awaits. Prepare for enlightenment.
        </p>
        <Link href="/"
          className="inline-block bg-amber-600 hover:bg-rose-600 text-stone-900 font-semibold px-8 py-3 rounded-lg transition-colors duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-opacity-50"
        >
          Return to the Forum (Home)
        </Link>
      </main>
      <footer className="w-full p-8 text-center mt-12">
        <p className="text-xs opacity-50">Promptus Maximus © 2024</p>
      </footer>
    </div>
  );
} 