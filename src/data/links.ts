export interface CuratedLink {
	title: string;
	url: string;
	description?: string;
}

export interface LinkGroup {
	title: string;
	links: CuratedLink[];
}

export const linkGroups: LinkGroup[] = [
	{
		title: "Classical music performances",
		links: [{
			title: "Faust Fantasy - Wieniawski (Kogan)",
			url: "https://www.youtube.com/watch?v=1ZzXyFMh-kQ&list=RD1ZzXyFMh-kQ&start_radio=1"
		},
		{
			title: "Sonata for Solo Violin No.5: Danse rustique - Ysaÿe (Sant'Anna)",
			url: "https://www.youtube.com/watch?v=JIK3v5qJJVA"
		},
		{
			title: "Violin Concerto - Dvořák (Fischer)",
			url: "https://www.youtube.com/watch?v=9rAd0-pTuU8"
		},
		{
			title: "Chant d'Amour - Suk (Szeryng)",
			url: "https://www.youtube.com/watch?v=E9E1e8sABZU&list=RDE9E1e8sABZU&start_radio=1"
		},
		{
			title: "Sinfonia Concertante - Mozart (Sitkovetsky, Ridout)",
			url: "https://www.youtube.com/watch?v=-JAAQqVnpR8&list=RD-JAAQqVnpR8&start_radio=1&t=1543s"
		},
		{
			title: "Violin Sonata No.1: Siciliano - Bach (Malov)",
			url: "https://www.youtube.com/watch?v=GutyYYcEXPA&list=RDGutyYYcEXPA&start_radio=1"
		},
		{
			title: "Violin Concerto - Sibelius (Haendel)",
			url: "https://www.youtube.com/watch?v=VYBQyOOED8k&list=RDVYBQyOOED8k&start_radio=1"
		},
		{
			title: "Gran Duo - Bottesini (Ibragimova, Ibragimov)",
			url: "https://www.youtube.com/watch?v=lm8W8jMtQyA&list=RDlm8W8jMtQyA&start_radio=1"
		}
	],
	},
	{
		title: "Books",
		links: [{
			title: "Chaos: Making a New Science (Gleick)",
			url: "https://en.wikipedia.org/wiki/Chaos:_Making_a_New_Science"
		},
		{
			title: "A Mathematician's Apology (Hardy)",
			url: "https://en.wikipedia.org/wiki/A_Mathematician%27s_Apology"
		}
	]
	},
	{
		title: "Textbooks",
		links: [],
	},
	{
		title: "Videos",
		links: [],
	},
];

// Add links using this shape:
// {
// 	title: "A link I like",
// 	url: "https://example.com",
// 	description: "A short optional note about why it is worth visiting.",
// }
