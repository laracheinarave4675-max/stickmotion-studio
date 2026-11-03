const VISUAL_ORDER = [
  ["space", /\b(space|universe|galaxy|planet|star|moon|mars|earth|cosmos|orbit|astronomical)\b/],
  ["night", /\b(dark|darkness|night|shadow|afraid|fear|scared|haunted|lights? (?:go|went) out)\b/],
  ["clock", /\b(time|clock|second|minute|hour|year|century|future|past|history|ancient|era)\b/],
  ["conversation", /\b(talk|talking|conversation|together|friend|people|someone|they|she|he|argue|discuss)\b/],
  ["journey", /\b(journey|travel|walk|walking|run|running|road|path|mountain|explore|cross|climb)\b/],
  ["science", /\b(question|why|how|brain|mind|idea|theory|science|discover|think|imagine|understand|experiment|evidence)\b/]
];

export function splitNarration(text) {
  return String(text ?? "")
    .replace(/\r/g, "")
    .split(/(?<=[.!?])\s+|\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

export function classifyScene(text) {
  const value = String(text ?? "").toLowerCase();
  let visual = "room";
  for (const [name, pattern] of VISUAL_ORDER) {
    if (pattern.test(value)) {
      visual = name;
      break;
    }
  }

  let mood = "explaining";
  if (/\b(fear|afraid|danger|threat|worry|worried|anxious|scared|haunted)\b/.test(value)) mood = "worried";
  else if (/\b(happy|joy|success|love|wonderful|amazing|hope|celebrate)\b/.test(value)) mood = "happy";
  else if (/\b(run|running|move|moving|quick|sudden|jump|journey|travel|climb)\b/.test(value)) mood = "active";
  else if (/\b(why|how|wonder|question|think|imagine|perhaps|maybe|curious)\b/.test(value)) mood = "thinking";

  const wordCount = value.match(/\S+/g)?.length ?? 0;
  const duration = Math.max(4, Math.min(9, Math.round(wordCount / 2.5)));
  return { visual, mood, duration };
}

export function makeTitle(text) {
  const title = String(text ?? "").replace(/[.!?]/g, "").split(/\s+/).filter(Boolean).slice(0, 7).join(" ");
  return title.length > 48 ? title.slice(0, 45) + "…" : title;
}

export function buildScenePlan(text) {
  return splitNarration(text).map((narration, index) => ({
    id: index + 1,
    narration,
    title: makeTitle(narration),
    ...classifyScene(narration)
  }));
}
