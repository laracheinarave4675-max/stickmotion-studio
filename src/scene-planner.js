const VISUAL_ORDER = [
  ["historical", /\b(history|historical|ancient|medieval|kingdom|empire|pharaoh|roman|egyptian|viking|castle|knight|dynasty|century|archaeolog|artifact|civilization|revolution)\b/],
  ["crime", /\b(murder|killer|crime|criminal|victim|suspect|homicide|serial|poison|blood|body|dead|death|assassin|robbery|theft|kidnap|missing person)\b/],
  ["investigation", /\b(detective|investigat|evidence|clue|fingerprint|interrogate|witness|case file|forensic|police|crime scene|mystery|questioned)\b/],
  ["prison", /\b(prison|jail|cell|escapee|guard|inmate|captiv|hostage|locked|confinement)\b/],
  ["desert", /\b(desert|sandstorm|dune|sahara|oasis|scorching|heatwave|camel|arid)\b/],
  ["shipwreck", /\b(shipwreck|ship|sinking|ocean|sea|island|raft|sailor|titanic|drown|storm at sea|castaway)\b/],
  ["wilderness", /\b(forest|jungle|wild|bear|wolf|snake|predator|mountain|cave|river|campfire|hunting|tracking)\b/],
  ["war", /\b(war|battle|soldier|army|weapon|siege|frontline|invasion|bomb|trench|general|combat|military)\b/],
  ["disaster", /\b(disaster|earthquake|flood|fire|wildfire|hurricane|tsunami|volcano|collapse|explosion|crash|catastrophe)\b/],
  ["survival", /\b(surviv|stranded|alone|starv|thirst|shelter|ration|rescue|lost|wilderness|escape|trapped|endure)\b/],
  ["night", /\b(dark|darkness|night|shadow|afraid|fear|scared|haunted|lights? (?:go|went) out)\b/],
  ["clock", /\b(time|clock|second|minute|hour|future|past|timeline|before|after)\b/],
  ["conversation", /\b(talk|talking|conversation|together|friend|people|someone|they|she|he|argue|discuss|said|asked|replied)\b/],
  ["journey", /\b(journey|travel|walk|walking|run|running|road|path|explore|cross|climb|escape route)\b/],
  ["science", /\b(question|why|how|brain|mind|idea|theory|science|discover|think|imagine|understand|experiment|evidence)\b/]
];

const PROP_RULES = [
  ["water bottle", /\b(water|canteen|bottle|thirst)\b/],
  ["map", /\b(map|route|compass|direction)\b/],
  ["rope", /\b(rope|climb|tied|knot)\b/],
  ["flashlight", /\b(flashlight|torch|darkness|dark|night)\b/],
  ["evidence folder", /\b(evidence|case file|document|investigat|clue)\b/],
  ["photograph", /\b(photo|photograph|picture|portrait)\b/],
  ["weapon", /\b(weapon|gun|rifle|sword|attack|battle|soldier)\b/],
  ["boat or raft", /\b(ship|boat|raft|ocean|sea|shipwreck|sinking)\b/],
  ["food or ration", /\b(food|eat|hungry|starv|ration)\b/],
  ["fire", /\b(fire|flame|burn|campfire)\b/],
  ["keys", /\b(key|locked|cell|door|escape)\b/],
  ["letter or note", /\b(letter|note|message|written|diary)\b/],
  ["clock", /\b(clock|time|hour|minute|deadline)\b/]
];

const ACTION_RULES = [\n  ["opening or unlocking", /\\b(open|opened|opening|unlock|unlocked|unlocked|turn the key)\\b/],\n  ["picking up or collecting", /\\b(pick up|picked up|grab|grabbed|collect|collected|lift|lifted)\\b/],\n  ["helping or rescuing", /\\b(help|helped|rescue|rescued|pull|pulled|carry|carried|drag|dragged)\\b/],\n  ["reaching or handing over", /\\b(reach|reached|hand|handed|give|gave|pass|passed)\\b/],
  ["running", /\b(run|ran|running|flee|fled|fleeing|chase|chased|chasing|escape|escaping)\b/],
  ["walking or travelling", /\b(walk|walking|travel|journey|march|cross|approach)\b/],
  ["searching for clues", /\b(search|searching|investigat|examine|inspect|look for|track|tracking)\b/],
  ["fighting", /\b(fight|fighting|attack|attacking|battle|combat|defend)\b/],
  ["hiding", /\b(hide|hiding|conceal|sneak|sneaking)\b/],
  ["climbing", /\b(climb|climbing|scramble|ascend)\b/],
  ["swimming or struggling in water", /\b(swim|swimming|drown|drowning|drift|floating|waves)\b/],
  ["building a shelter", /\b(shelter|build|building|construct|camp)\b/],
  ["sitting or waiting", /\b(sit|sitting|wait|waiting|rest|resting)\b/],
  ["speaking or arguing", /\b(said|say|asked|replied|shout|shouted|whisper|argue|discuss|talk)\b/],
  ["discovering or revealing", /\b(found|discover|revealed|uncovered|realized|noticed)\b/],
  ["falling or collapsing", /\b(fall|falling|collapse|collapsed|crash)\b/]
];

const SETTING_LABELS = {
  historical: "historical location or period setting", crime: "crime scene",
  investigation: "detective investigation room", prison: "prison cell or corridor",
  desert: "open desert landscape", shipwreck: "open sea and damaged vessel",
  wilderness: "remote wilderness", war: "battlefield", disaster: "disaster-affected location",
  survival: "remote survival environment", night: "dark nighttime setting",
  clock: "symbolic timeline setting", conversation: "simple conversation setting",
  journey: "road or travel landscape", science: "explanatory visual space", room: "neutral interior"
};

function firstMatch(value, rules, fallback) {
  for (const [label, pattern] of rules) if (pattern.test(value)) return label;
  return fallback;
}

export function splitNarration(text) {
  return String(text ?? "").replace(/\r/g, "").split(/(?<=[.!?])\s+|\n+/).map((part) => part.trim()).filter(Boolean);
}

export function classifyScene(text) {
  const value = String(text ?? "").toLowerCase();
  const visual = firstMatch(value, VISUAL_ORDER, "room");
  let mood = "explaining";
  if (/\b(fear|afraid|danger|threat|worry|worried|anxious|scared|haunted|terrified|panic|desperate)\b/.test(value)) mood = "worried";
  else if (/\b(happy|joy|success|love|wonderful|amazing|hope|celebrate|victory|relief)\b/.test(value)) mood = "happy";
  else if (/\b(run|running|move|moving|quick|sudden|jump|journey|travel|climb|escape|fight|attack|struggle)\b/.test(value)) mood = "active";
  else if (/\b(why|how|wonder|question|think|imagine|perhaps|maybe|curious|investigate|discover|realized)\b/.test(value)) mood = "thinking";
  const wordCount = value.match(/\S+/g)?.length ?? 0;
  const duration = Math.max(4, Math.min(9, Math.round(wordCount / 2.5)));
  const action = firstMatch(value, ACTION_RULES, "observing or explaining");
  const props = PROP_RULES.filter(([, pattern]) => pattern.test(value)).map(([label]) => label);
  const camera = mood === "active" ? "wide action shot with a slight tracking move"
    : mood === "worried" ? "tight medium shot emphasizing the character's expression"
    : visual === "investigation" || visual === "crime" ? "slow push-in toward the important clue"
    : visual === "historical" || visual === "war" || visual === "disaster" ? "wide establishing shot, then medium character shot"
    : "medium shot with a clear view of the setting and relevant prop";
  const transition = mood === "active" ? "match cut or quick directional cut"
    : mood === "worried" ? "slow dissolve" : "clean cut";
  return { visual, mood, duration, setting: SETTING_LABELS[visual], action, props, camera, transition };
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
