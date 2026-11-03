const VISUAL_ORDER = [
  ["historical", /\b(history|historical|ancient|medieval|kingdom|empire|pharaoh|roman|egyptian|viking|castle|knight|dynasty|century|archaeolog|artifact|civilization|revolution)\b/],
  ["crime", /\b(murder|killer|crime|criminal|victim|suspect|homicide|serial|poison|blood|body|dead|death|assassin|robbery|theft|kidnap|missing person)\b/],
  ["investigation", /\b(detective|investigat|evidence|clue|fingerprint|interrogate|witness|case file|forensic|police|crime scene|mystery|questioned)\b/],
  ["prison", /\b(prison|jail|cell|escapee|guard|inmate|captiv|hostage|locked|confinement)\b/],
  ["survival", /\b(surviv|stranded|alone|starv|thirst|shelter|ration|rescue|lost|wilderness|escape|trapped|endure)\b/],
  ["desert", /\b(desert|sandstorm|dune|sahara|oasis|scorching|heatwave|camel|arid)\b/],
  ["shipwreck", /\b(shipwreck|ship|sinking|ocean|sea|island|raft|sailor|titanic|drown|storm at sea|castaway)\b/],
  ["wilderness", /\b(forest|jungle|wild|bear|wolf|snake|predator|mountain|cave|river|campfire|hunting|tracking)\b/],
  ["war", /\b(war|battle|soldier|army|weapon|siege|frontline|invasion|bomb|trench|general|combat|military)\b/],
  ["disaster", /\b(disaster|earthquake|flood|fire|wildfire|hurricane|tsunami|volcano|collapse|explosion|crash|catastrophe)\b/],
  ["night", /\b(dark|darkness|night|shadow|afraid|fear|scared|haunted|lights? (?:go|went) out)\b/],
  ["clock", /\b(time|clock|second|minute|hour|future|past|timeline|before|after)\b/],
  ["conversation", /\b(talk|talking|conversation|together|friend|people|someone|they|she|he|argue|discuss|said|asked|replied)\b/],
  ["journey", /\b(journey|travel|walk|walking|run|running|road|path|explore|cross|climb|escape route)\b/],
  ["science", /\b(question|why|how|brain|mind|idea|theory|science|discover|think|imagine|understand|experiment|evidence)\b/]
];

export function splitNarration(text) {
  return String(text ?? "").replace(/\r/g, "").split(/(?<=[.!?])\s+|\n+/).map((part) => part.trim()).filter(Boolean);
}

export function classifyScene(text) {
  const value = String(text ?? "").toLowerCase();
  let visual = "room";
  for (const [name, pattern] of VISUAL_ORDER) {
    if (pattern.test(value)) { visual = name; break; }
  }
  let mood = "explaining";
  if (/\b(fear|afraid|danger|threat|worry|worried|anxious|scared|haunted|terrified|panic)\b/.test(value)) mood = "worried";
  else if (/\b(happy|joy|success|love|wonderful|amazing|hope|celebrate|victory)\b/.test(value)) mood = "happy";
  else if (/\b(run|running|move|moving|quick|sudden|jump|journey|travel|climb|escape|fight|attack)\b/.test(value)) mood = "active";
  else if (/\b(why|how|wonder|question|think|imagine|perhaps|maybe|curious|investigate|discover)\b/.test(value)) mood = "thinking";
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
    id: index + 1, narration, title: makeTitle(narration), ...classifyScene(narration)
  }));
}
