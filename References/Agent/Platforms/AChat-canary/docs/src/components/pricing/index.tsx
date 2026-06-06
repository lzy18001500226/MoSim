"use client";

import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Check, Plus, Minus, ExternalLink } from "lucide-react";
// import { Disclosure } from "@headlessui/react";
import Link from "next/link";
// import { Header } from "@/components/Header";
import { HomeSection } from "@/components/landing/home-section";
import { cn } from "@/lib/utils";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { CheckIcon, MinusIcon } from "lucide-react";
import React from "react";
import { tiers } from "./tiers";
import { type DeploymentOption, deploymentOptions } from "./options";
import { sections } from "./sections";

export default function Pricing({
	isPricingPage = false,
	initialVariant = "cloud",
}: {
	isPricingPage?: boolean;
	initialVariant?: "cloud" | "selfHosted";
}) {
	const [variant, setVariant] = useState<"cloud" | "selfHosted">(
		initialVariant,
	);
	const selectedTiers = tiers[variant];

	const InfoLink = ({ href }: { href: string }) => (
		<Link href={href} className="inline-block" target="_blank">
			<ExternalLink className="size-4 ml-2 pt-0.5" />
		</Link>
	);

	return (
		<HomeSection className={cn(isPricingPage && "px-0 sm:px-0")}>
			<div className="isolate overflow-hidden">
				<div className="flow-root pb-16 lg:pb-0">
					<div className="mx-auto max-w-7xl">
						{/* <Header
							title={deploymentOptions[variant].title}
							description={deploymentOptions[variant].subtitle}
							h="h1"
						/> */}

						{/* Deployment Options Tabs */}
						<Tabs
							defaultValue={variant}
							value={variant}
							className="mt-4 flex justify-center"
							onValueChange={(value) => {
								setVariant(value as "cloud" | "selfHosted");
							}}
						>
							<TabsList className="mx-auto">
								{Object.keys(deploymentOptions).map((key) => (
									<TabsTrigger key={key} value={key}>
										{deploymentOptions[key as DeploymentOption].switch}
									</TabsTrigger>
								))}
							</TabsList>
						</Tabs>

						{/* Pricing Cards Grid */}
						<div
							className={cn(
								"mt-12 grid sm:grid-cols-2 gap-y-6 gap-x-6 md:gap-x-2 lg:gap-x-6 lg:items-stretch",
								selectedTiers.length === 4 && "md:grid-cols-4",
								selectedTiers.length === 3 && "md:grid-cols-3",
								selectedTiers.length === 2 && "md:grid-cols-2",
							)}
						>
							{selectedTiers.map((tier) => (
								<Card
									key={tier.id}
									className={cn(
										tier.featured && "border-primary",
										"relative h-full flex flex-col",
									)}
								>
									<CardHeader className="p-4 lg:p-6 text-left">
										<CardTitle className="text-lg text-foreground font-semibold">
											{tier.name}
										</CardTitle>
										<CardDescription className="text-left md:min-h-20 lg:min-h-16">
											{tier.description}
											{tier.learnMore && (
												<>
													{" "}
													<Link href={tier.learnMore} className="underline">
														Learn more
													</Link>
													.
												</>
											)}
										</CardDescription>
									</CardHeader>
									<CardContent className="p-0 px-4 lg:px-6 mb-4">
										<Button
											className="w-full"
											variant={tier.featured ? "default" : "outline"}
											asChild
										>
											<Link href={tier.href}>{tier.cta}</Link>
										</Button>
									</CardContent>
									<CardFooter className="p-4 lg:p-6 flex-col items-start gap-2">
										<div>
											<span className="font-bold text-3xl">{tier.price}</span>
											{tier.price.includes("$") && (
												<span className="text-sm leading-4 mt-2">
													{tier.priceUnit ? `/ ${tier.priceUnit}` : "/ 月"}
												</span>
											)}
										</div>
										<ul className="mt-3 space-y-2.5 text-sm">
											{tier.mainFeatures.map((feature) => (
												<li key={feature} className="flex space-x-2">
													<Check className="flex-shrink-0 mt-0.5 h-4 w-4 text-primary" />
													<span className="text-muted-foreground">
														{feature}
													</span>
												</li>
											))}
										</ul>
									</CardFooter>
								</Card>
							))}
						</div>

						{isPricingPage && (
							<>
								{/* Feature comparison (up to lg) */}
								<section
									aria-labelledby="mobile-comparison-heading"
									className="lg:hidden mt-20"
								>
									<h2 id="mobile-comparison-heading" className="sr-only">
										Feature comparison
									</h2>

									<div className="mx-auto max-w-2xl space-y-16">
										{selectedTiers.map((tier) => (
											<div
												key={tier.id}
												className="mb-10 bg-card rounded-lg overflow-hidden border p-4"
											>
												<div className="mb-6">
													<h4 className="text-lg text-foreground font-semibold">
														{tier.name}
													</h4>
													<p className="mt-2 text-sm text-muted-foreground">
														{tier.description}
													</p>
												</div>
												<Table>
													<TableBody>
														{sections.map((section) => (
															<React.Fragment key={section.name}>
																<TableRow className="bg-muted hover:bg-muted">
																	<TableCell
																		colSpan={2}
																		className="w-10/12 text-primary font-bold"
																	>
																		{section.name}
																		{section.href && (
																			<InfoLink href={section.href} />
																		)}
																	</TableCell>
																</TableRow>
																{section.features
																	.filter((f) => variant in f.tiers)
																	.map((feature) => (
																		<TableRow
																			key={feature.name}
																			className="text-muted-foreground"
																		>
																			<TableCell className="w-11/12">
																				{feature.name}
																				{feature.href && (
																					<InfoLink href={feature.href} />
																				)}
																			</TableCell>
																			<TableCell>
																				{typeof feature.tiers[variant]?.[
																					tier.name
																				] === "string" ? (
																					<div className="text-sm leading-6 text-center">
																						{feature.tiers[variant]?.[tier.name]}
																					</div>
																				) : (
																					<div className="flex justify-center">
																						{feature.tiers[variant]?.[
																							tier.name
																						] === true ? (
																							<CheckIcon className="h-5 w-5 text-primary" />
																						) : (
																							<MinusIcon className="h-5 w-5 text-muted-foreground" />
																						)}
																					</div>
																				)}
																			</TableCell>
																		</TableRow>
																	))}
															</React.Fragment>
														))}
													</TableBody>
												</Table>
											</div>
										))}
									</div>
								</section>

								{/* Feature comparison (lg+) */}
								<section
									aria-labelledby="comparison-heading"
									className="hidden lg:block bg-card rounded-lg overflow-hidden border mt-20"
								>
									<h2 id="comparison-heading" className="sr-only">
										Feature comparison
									</h2>

									<Table className="w-full">
										<TableHeader className="bg-background">
											<TableRow className="bg-muted hover:bg-muted">
												<TableHead className="w-3/12" />
												{selectedTiers.map((tier) => (
													<TableHead
														key={tier.id}
														className="w-2/12 text-center text-lg text-foreground font-semibold"
													>
														{tier.name}
													</TableHead>
												))}
											</TableRow>
										</TableHeader>
										<TableBody>
											{sections.map((section) => (
												<React.Fragment key={section.name}>
													<TableRow className="bg-muted/50">
														<TableCell colSpan={5} className="font-medium">
															{section.name}
															{section.href && <InfoLink href={section.href} />}
														</TableCell>
													</TableRow>
													{section.features
														.filter((f) => variant in f.tiers)
														.map((feature) => (
															<TableRow
																key={feature.name}
																className="text-muted-foreground"
															>
																<TableCell>
																	{feature.name}
																	{feature.href && (
																		<InfoLink href={feature.href} />
																	)}
																</TableCell>
																{selectedTiers.map((tier) => (
																	<TableCell key={tier.id}>
																		{(() => {
																			const value = feature.tiers[variant]?.[tier.name];
																			if (typeof value === "string") {
																				return (
																					<div className="text-sm leading-6 text-center">
																						{value}
																					</div>
																				);
																			}
																			return (
																				<div className="flex justify-center">
																					{value === true ? (
																						<CheckIcon className="h-5 w-5 text-primary" />
																					) : (
																						<MinusIcon className="h-5 w-5 text-muted-foreground" />
																					)}
																				</div>
																			);
																		})()}
																	</TableCell>
																))}
															</TableRow>
														))}
												</React.Fragment>
											))}
										</TableBody>
									</Table>
								</section>
							</>
						)}
					</div>
				</div>
				{/* {isPricingPage ? (
					<>
						<div className="relative">
							<div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
								<DiscountOverview className="mt-10" />
								<PricingFAQ />
							</div>
						</div>
					</>
				) : (
					<>
						<div className="text-center mt-10">
							For a detailed comparison and FAQ, see our{" "}
							<Link
								href={deploymentOptions[variant].href}
								className="underline"
							>
								pricing page
							</Link>
							.
						</div>
					</>
				)} */}
			</div>
		</HomeSection>
	);
}
