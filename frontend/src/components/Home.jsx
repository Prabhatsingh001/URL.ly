import React from "react";

const samplePosts = [
	{
		id: 1,
		title: "Launching My Tech Blog",
		excerpt: "A quick introduction to the blog — what to expect and why I started it.",
		date: "Dec 10, 2025",
		tag: "Announcements",
	},
	{
		id: 2,
		title: "Improving Web Performance",
		excerpt: "Practical tips to speed up your web apps and improve user experience.",
		date: "Nov 28, 2025",
		tag: "Web",
	},
	{
		id: 3,
		title: "Tailwind CSS for Rapid UI",
		excerpt: "Why Tailwind speeds up development and how to use it effectively.",
		date: "Oct 05, 2025",
		tag: "CSS",
	},
];

export default function Home() {
	return (
		<div className="min-h-screen bg-gray-50 text-gray-900">
			<header className="bg-white shadow">
				<div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
					<h1 className="text-2xl font-extrabold tracking-tight">My Blog</h1>
					<nav className="space-x-4">
						<a className="text-sm font-medium text-gray-600 hover:text-gray-900" href="#posts">Posts</a>
						<a className="text-sm font-medium text-gray-600 hover:text-gray-900" href="#about">About</a>
						<a className="text-sm font-medium text-gray-600 hover:text-gray-900" href="#subscribe">Subscribe</a>
					</nav>
				</div>
			</header>

			<main>
				<section className="relative overflow-hidden bg-linear-to-br from-slate-900 via-indigo-800 to-indigo-600 text-white">
					<div className="absolute inset-0 opacity-20 bg-linear-to-tr from-white/20 via-transparent to-white/5" aria-hidden="true" />
					<div className="max-w-6xl mx-auto px-6 py-20 lg:py-28 relative">
						<div className="lg:w-3/4 space-y-6">
							<div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 border border-white/20 rounded-full text-sm font-medium">New • Essays and tutorials</div>
							<h2 className="text-4xl sm:text-5xl font-extrabold leading-tight">Thoughts, tutorials, and experiments for modern web builders.</h2>
							<p className="text-lg text-indigo-100/90">I share hands-on notes on performance, design systems, product engineering, and the workflows that keep teams shipping.</p>
							<div className="flex flex-wrap gap-3">
								<a href="#posts" className="inline-flex items-center px-5 py-3 bg-white text-indigo-800 rounded-md font-semibold shadow hover:translate-y-0.5 transition">Read the latest</a>
								<a href="#subscribe" className="inline-flex items-center px-5 py-3 border border-white/30 text-white rounded-md font-semibold hover:bg-white/10">Subscribe</a>
							</div>
							<div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-indigo-100/80">
								<div className="p-4 bg-white/5 rounded-lg border border-white/10">Actionable guides</div>
								<div className="p-4 bg-white/5 rounded-lg border border-white/10">Performance deep-dives</div>
								<div className="p-4 bg-white/5 rounded-lg border border-white/10">Tooling breakdowns</div>
							</div>
						</div>
					</div>
				</section>

				<section id="posts" className="max-w-6xl mx-auto px-6 py-12">
					<div className="flex items-center justify-between">
						<h3 className="text-2xl font-bold">Latest posts</h3>
						<a href="#" className="text-sm font-semibold text-indigo-700 hover:text-indigo-900">View all</a>
					</div>

					<div className="mt-6 grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
						{samplePosts.map((post) => (
							<article key={post.id} className="bg-white border border-gray-100 rounded-xl p-6 shadow-[0_10px_40px_-24px_rgba(0,0,0,0.35)] hover:shadow-[0_14px_50px_-22px_rgba(0,0,0,0.35)] transition">
								<div className="flex items-baseline justify-between">
									<span className="inline-flex items-center px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide bg-indigo-50 text-indigo-700 rounded">{post.tag}</span>
									<time className="text-xs text-gray-400">{post.date}</time>
								</div>
								<h4 className="mt-4 text-lg font-semibold text-gray-900 leading-snug">{post.title}</h4>
								<p className="mt-2 text-sm text-gray-600 leading-relaxed">{post.excerpt}</p>
								<div className="mt-5">
									<a className="text-sm font-semibold text-indigo-700 hover:text-indigo-900" href="#">Read article →</a>
								</div>
							</article>
						))}
					</div>
				</section>

				<section id="about" className="bg-white border-t border-b border-gray-100">
					<div className="max-w-4xl mx-auto px-6 py-12 space-y-4">
						<h3 className="text-2xl font-bold">About this blog</h3>
						<p className="text-gray-600 leading-relaxed">This blog captures lessons learned building web products, short tutorials, and curated links. Posts are published irregularly — subscribe to get updates.</p>
						<div className="flex flex-wrap gap-2 text-sm">
							<span className="px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 font-medium">Performance</span>
							<span className="px-3 py-1 rounded-full bg-sky-50 text-sky-700 font-medium">Design systems</span>
							<span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 font-medium">Tooling</span>
							<span className="px-3 py-1 rounded-full bg-amber-50 text-amber-700 font-medium">Product</span>
						</div>
					</div>
				</section>

				<section id="subscribe" className="max-w-3xl mx-auto px-6 py-12">
					<div className="bg-linear-to-r from-white to-indigo-50 border border-gray-100 rounded-xl p-8 shadow-sm">
						<h4 className="text-xl font-semibold">Stay in the loop</h4>
						<p className="mt-2 text-sm text-gray-600">Get new posts delivered to your inbox once or twice a month.</p>
						<form className="mt-4 sm:flex sm:items-center gap-3">
							<label htmlFor="email" className="sr-only">Email</label>
							<input id="email" type="email" placeholder="you@domain.com" className="w-full sm:flex-1 px-4 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400" />
							<button type="submit" className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold hover:bg-indigo-700">Subscribe</button>
						</form>
					</div>
				</section>
			</main>

			<footer className="mt-12 bg-white border-t border-gray-100">
				<div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between">
					<p className="text-sm text-gray-500">© {new Date().getFullYear()} My Blog — Built with Tailwind CSS</p>
					<div className="mt-3 sm:mt-0 space-x-4">
						<a className="text-sm text-gray-500 hover:text-gray-700" href="#">Privacy</a>
						<a className="text-sm text-gray-500 hover:text-gray-700" href="#">Contact</a>
					</div>
				</div>
			</footer>
		</div>
	);
}

