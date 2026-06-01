const faqs = [
	{
		question: "What is the easiest way to try Langfuse?",
		answer:
			"You can view the <a class='underline' href='/demo'>public demo project</a> or sign up for a <a class='underline' href='https://cloud.langfuse.com'>free account</a> to try Langfuse with your own data. The Hobby plan is completeley free and does not require a credit card.",
	},
	{
		question: "What is an observation?",
		answer:
			"Traces in Langfuse include a set of observations. An observation is a single event that occurred in your system. For example, a single LLM call, a single HTTP request, a single log object, or a database query. Check out the <a class='underline' href='/docs/tracing-data-model'>Langfuse Data Model docs<a/> for more details.",
	},
	{
		question: "Can I self-host Langfuse?",
		answer:
			"Yes, Langfuse is open source and you can run Langfuse <a class='underline' href='/self-hosting/local'>locally using docker compose<a/> or for <a class='underline' href='/self-hosting'>production use via docker<a/> and a standalone database.",
	},
	{
		question: "Where is the data stored?",
		answer:
			"Langfuse Cloud is hosted on AWS and data is stored in the US or EU depending on your selection. See our <a class='underline' href='/docs/data-security-privacy'>security and privacy documentation</a> for more details.",
	},
	{
		question: "Do you offer discounts?",
		answer:
			"Yes, we offer discounts for startups (request <a class='underline' href='https://forms.gle/eJAYjRWeCZU1Mn6j8'>here</a>), students, academics and open-source projects. If you believe your situation warrants a discount, please contact us at support@langfuse.com with details about your project.",
	},
	{
		question: "How do I activate my self-hosted Pro or Enterprise plan?",
		answer:
			"Once you've deployed Langfuse OSS, you can activate your Pro or Enterprise plan by adding the license key you received from the Langfuse team to your deployment.",
	},
	{
		question: "How can I manage my subscription?",
		answer:
			"You can manage your subscription through the organization settings in Langfuse Cloud or by using this <a class='underline' href='/billing-portal'>Customer Portal</a> for both Langfuse Cloud and Self-Hosted subscriptions.",
	},
	{
		question: "Can I redline the contracts?",
		answer:
			"Yes, we do offer customized contracts as an add-on on Langfuse Teams (cloud) and as a part of an Enterprise agreement (self-hosted). Please contact us at enterprise@langfuse.com for more details. The default plans are affordable as they are designed to be self-serve on our standard terms.",
	},
	{
		question: "Do you offer billing via AWS Marketplace?",
		answer:
			"Yes, all Langfuse Enterprise plans are available via AWS Marketplace (private offer). This applies to both Langfuse Cloud and Self-Hosted deployments. Please contact us at enterprise@langfuse.com for more details.",
	},
];

// export function PricingFAQ() {
// 	return (
// 		<div id="faq">
// 			<div className="mx-auto max-w-7xl px-6 pb-24 pt-16 lg:px-8">
// 				<div className="mx-auto max-w-4xl divide-y divide-primary/10">
// 					<h2 className="text-2xl font-bold leading-10 tracking-tight text-primary">
// 						Frequently asked questions
// 					</h2>
// 					<dl className="mt-10 space-y-6 divide-y divide-primary/10">
// 						{faqs.map((faq) => (
// 							<Disclosure as="div" key={faq.question} className="pt-6">
// 								{({ open }) => (
// 									<>
// 										<dt>
// 											<Disclosure.Button className="flex w-full items-start justify-between text-left text-primary">
// 												<span className="text-base font-semibold leading-7">
// 													{faq.question}
// 												</span>
// 												<span className="ml-6 flex h-7 items-center">
// 													{open ? (
// 														<Minus className="h-6 w-6" aria-hidden="true" />
// 													) : (
// 														<Plus className="h-6 w-6" aria-hidden="true" />
// 													)}
// 												</span>
// 											</Disclosure.Button>
// 										</dt>
// 										<Disclosure.Panel as="dd" className="mt-2 pr-12">
// 											<p
// 												className="text-base leading-7 text-primary/70"
// 												dangerouslySetInnerHTML={{ __html: faq.answer }}
// 											/>
// 										</Disclosure.Panel>
// 									</>
// 								)}
// 							</Disclosure>
// 						))}
// 					</dl>
// 				</div>
// 			</div>
// 		</div>
// 	);
// }
