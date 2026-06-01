"use client";

import { useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";

export function DatabasePassword({ children }: { children: React.ReactNode }) {
	const ref = useRef<HTMLDivElement>(null);
	const nameRef = useRef<HTMLElement>(null);
	const portRef = useRef<HTMLElement>(null);
	const volumeRef = useRef<HTMLElement>(null);
	const passwordRef = useRef<HTMLElement>(null);

	useEffect(() => {
		if (ref.current) {
			if (!nameRef.current) {
				const token = [...ref.current.querySelectorAll("code span")].find(
					(el) => (el as HTMLElement).innerText === " vmboard-db",
				);
				nameRef.current = token as HTMLElement;
			}
			if (!portRef.current) {
				const token = [...ref.current.querySelectorAll("code span")].find(
					(el) => (el as HTMLElement).innerText === " 5432:5432",
				);
				portRef.current = token as HTMLElement;
			}
			if (!volumeRef.current) {
				const token = [...ref.current.querySelectorAll("code span")].find(
					(el) =>
						(el as HTMLElement).innerText ===
						" vmboard-db-data:/home/postgres/pgdata/data",
				);
				volumeRef.current = token as HTMLElement;
			}
			if (!passwordRef.current) {
				const token = [...ref.current.querySelectorAll("code span")].find(
					(el) =>
						(el as HTMLElement).innerText === " POSTGRES_PASSWORD=postgres",
				);
				passwordRef.current = token as HTMLElement;
			}
		}
	}, []);

	return (
		<div ref={ref} style={{ marginTop: "1.5rem" }}>
			<div className="grid grid-cols-4 gap-2">
				<Input
					placeholder="vmboard-db"
					onInput={(e) => {
						if (!nameRef.current) return;
						if (e.currentTarget.value.trim().length === 0) {
							nameRef.current.innerText = " vmboard-db";
						} else {
							nameRef.current.innerText = ` ${e.currentTarget.value}`;
						}
					}}
				/>
				<Input
					placeholder="5432"
					onInput={(e) => {
						if (!portRef.current) return;
						if (e.currentTarget.value.trim().length === 0) {
							portRef.current.innerText = " 5432:5432";
						} else {
							portRef.current.innerText = ` ${e.currentTarget.value}:5432`;
						}
					}}
				/>
				<Input
					placeholder="vmboard-db-data"
					onInput={(e) => {
						if (!volumeRef.current) return;
						if (e.currentTarget.value.trim().length === 0) {
							volumeRef.current.innerText = " vmboard-db-data:/home/postgres/pgdata/data";
						} else {
							volumeRef.current.innerText = ` ${e.currentTarget.value}:/home/postgres/pgdata/data`;
						}
					}}
				/>
				<Input
					placeholder="postgres"
					onInput={(e) => {
						if (!passwordRef.current) return;
						if (e.currentTarget.value.trim().length === 0) {
							passwordRef.current.innerText = " POSTGRES_PASSWORD=postgres";
						} else {
							passwordRef.current.innerText = ` POSTGRES_PASSWORD=${e.currentTarget.value}`;
						}
					}}
				/>
			</div>
			{children}
		</div>
	);
}
