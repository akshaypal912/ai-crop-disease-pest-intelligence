import type { DiseaseLibraryEntry } from '../types/diseaseLibrary';

/** Educational reference content — not live AI predictions. */
export const DISEASE_LIBRARY: DiseaseLibraryEntry[] = [
  {
    id: 'tomato-leaf-blight',
    name: 'Tomato Leaf Blight',
    crop: 'Tomato',
    category: 'Disease',
    image: '/assets/tomato_late_blight.jpg',
    sampleId: 'sample-1',
    shortDescription: 'Dark, water-soaked spots on tomato leaves that can spread quickly in wet weather.',
    overview:
      'Tomato leaf blight refers to serious leaf infections (often late blight) that create dark lesions on foliage. Infected leaves may wilt and die, reducing yield. This page is general educational information — not a diagnosis from your field.',
    symptoms: [
      'Irregular brown or black patches on leaves, sometimes with a lighter edge',
      'Water-soaked or oily-looking spots that enlarge in humid weather',
      'Yellowing around lesions and browning of leaf tips',
      'White fungal growth on leaf undersides during cool, wet periods',
    ],
    causes: [
      'Fungal or fungal-like pathogens spread by wind, rain splash, and infected plant material',
      'Carry-over on seed potatoes, volunteer plants, or crop debris',
      'Dense planting that keeps leaves wet for long periods',
    ],
    favorableConditions: {
      temperature: 'Cool to mild (roughly 15–24°C) favours many blight outbreaks',
      humidity: 'High humidity or long periods above 85% relative humidity',
      moisture: 'Frequent rain, dew, or overhead irrigation that keeps leaves wet',
      other: ['Poor airflow between rows', 'Nitrogen-rich lush canopy', 'Infected neighbouring plots'],
    },
    severity: 'High',
    severityExplanation:
      'High severity means the condition can spread fast across a tomato plot within days under wet weather, damaging leaves and fruit. Early scouting and local agronomic advice are important.',
    prevention: [
      'Use certified healthy seedlings and rotate away from tomato or potato in the same bed',
      'Improve row spacing and pruning for better air movement',
      'Avoid working in the field when foliage is wet',
      'Remove and destroy badly infected lower leaves away from the field',
    ],
    management: [
      'Scout lower and inner leaves twice weekly during cloudy, rainy spells',
      'Improve drainage and reduce leaf wetness where possible',
      'If sprays are needed, choose products registered for tomato in your state and follow label rates — consult your local Krishi Vigyan Kendra or agriculture officer',
      'Do not compost heavily infected plants',
    ],
    whenToAct:
      'Inspect within 24–48 hours if you see spreading dark lesions or after several days of rain. Contact an agriculture extension worker if more than a few plants show similar symptoms.',
    detectionNotes:
      'FarmEye AI can highlight suspicious leaf areas from a clear photo, but results are decision support only. Always confirm with field scouting and expert advice.',
    metaDescription:
      'Learn about Tomato Leaf Blight symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'potato-early-blight',
    name: 'Potato Early Blight',
    crop: 'Potato',
    category: 'Disease',
    image:
      'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-2',
    shortDescription: 'Target-like rings on older potato leaves, common in warm seasons with morning dew.',
    overview:
      'Early blight is a common potato leaf disease that starts on older leaves as brown spots with concentric rings. It usually progresses slowly but can weaken plants if ignored. Educational information only.',
    symptoms: [
      'Small brown spots with dark rings (target-board pattern)',
      'Yellow halos around spots on lower leaves first',
      'Premature yellowing and drop of older leaves',
      'Lesions may join into larger dead areas in severe cases',
    ],
    causes: [
      'Fungal spores surviving in crop residue and soil',
      'Splashing rain spreading spores to new leaves',
      'Plants stressed by heat, drought, or nutrient imbalance',
    ],
    favorableConditions: {
      temperature: 'Warm days around 24–29°C',
      humidity: 'Moderate to high humidity, especially overnight',
      moisture: 'Morning dew or light frequent rains',
      other: ['Continuous potato cropping', 'Shaded lower canopy', 'Wounded or senescing leaves'],
    },
    severity: 'Moderate',
    severityExplanation:
      'Moderate severity means yield impact is often limited if caught early on lower leaves, but the disease can move up the plant during long wet periods.',
    prevention: [
      'Rotate potatoes with non-host crops where possible',
      'Remove or bury old vines after harvest',
      'Maintain balanced fertilisation — avoid excess nitrogen',
      'Use disease-free seed tubers from trusted sources',
    ],
    management: [
      'Remove heavily spotted lower leaves if practical',
      'Irrigate at soil level to keep foliage dry',
      'Apply protectant fungicides only per local recommendations and product labels',
      'Monitor upper leaves weekly after flowering',
    ],
    whenToAct:
      'Begin scouting when lower leaves show the first ring spots. Seek advice if spots reach mid-canopy before tuber bulking.',
    detectionNotes:
      'Upload a sharp photo of affected potato leaves. FarmEye AI may suggest similar patterns but cannot replace laboratory or expert confirmation.',
    metaDescription:
      'Learn about Potato Early Blight, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'corn-leaf-rust',
    name: 'Corn Leaf Rust',
    crop: 'Corn / Maize',
    category: 'Disease',
    image:
      'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-3',
    shortDescription: 'Raised rust-coloured pustules on corn leaves, often seen in humid growing seasons.',
    overview:
      'Common rust appears as small raised pustules on corn leaves. Many hybrids tolerate light infection, but heavy rust can reduce photosynthesis. This summary is for learning, not a field diagnosis.',
    symptoms: [
      'Tiny cinnamon-brown or golden pustules on upper leaf surface',
      'Yellowing around dense pustule clusters',
      'Powdery orange-brown spores on fingers when rubbed',
      'Upper leaves affected later in the season',
    ],
    causes: [
      'Wind-borne fungal spores from infected corn or alternate hosts',
      'Carry-over in crop debris in mild climates',
      'Susceptible varieties without rust tolerance',
    ],
    favorableConditions: {
      temperature: 'Mild to warm (about 16–26°C)',
      humidity: 'High humidity with dew-heavy nights',
      moisture: 'Light rains and long leaf wetness periods',
      other: ['Late-planted corn', 'Dense planting', 'Early vegetative to mid-season growth stages'],
    },
    severity: 'Moderate',
    severityExplanation:
      'Moderate severity reflects that early rust often causes limited loss, but heavy infection on the ear leaf before grain fill can reduce yield.',
    prevention: [
      'Choose rust-tolerant hybrids suited to your region',
      'Avoid very late planting when rust pressure is historically high',
      'Rotate with non-host crops where practical',
      'Remove volunteer corn before the main season',
    ],
    management: [
      'Scout weekly — note percent of plants with pustules',
      'Fungicide is usually considered only if rust spreads above the ear leaf before tasseling — follow local extension thresholds',
      'Ensure balanced nutrition and timely irrigation',
      'Keep records for next season hybrid selection',
    ],
    whenToAct:
      'Check fields after warm, humid weather. Consult an agronomist if rust is widespread on the upper canopy before pollination.',
    detectionNotes:
      'FarmEye AI can help you document leaf symptoms from photos; always combine with field counts and local rust advisories.',
    metaDescription:
      'Learn about Corn Leaf Rust, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'apple-scab-lesion',
    name: 'Apple Scab Lesion',
    crop: 'Apple',
    category: 'Disease',
    image:
      'https://images.unsplash.com/photo-1567306301408-9b74779a11af?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-4',
    shortDescription: 'Olive-green velvety spots on apple leaves and fruit in cool, wet spring weather.',
    overview:
      'Apple scab causes dark, velvety lesions on leaves and young fruit. It is favoured by spring rains and can defoliate trees if unmanaged. Educational content — not an automated orchard diagnosis.',
    symptoms: [
      'Olive-green to brown velvety spots on leaves',
      'Misshapen or cracked fruit with scabby patches',
      'Yellowing and early leaf drop in severe cases',
      'Feathery lesion edges on young leaves',
    ],
    causes: [
      'Fungal spores released from infected leaves on the orchard floor',
      'Primary infection during spring rains',
      'Secondary spread within the canopy during wet periods',
    ],
    favorableConditions: {
      temperature: 'Cool spring temperatures (about 10–20°C)',
      humidity: 'High humidity with extended leaf wetness',
      moisture: 'Frequent spring rain or overhead sprinklers on foliage',
      other: ['Unpruned dense canopy', 'Fallen infected leaves not removed', 'Susceptible varieties'],
    },
    severity: 'High',
    severityExplanation:
      'High severity indicates scab can damage both foliage and fruit quality in wet springs, affecting marketable yield and tree health.',
    prevention: [
      'Plant scab-resistant varieties where available',
      'Shred and remove fallen leaves in autumn',
      'Prune for open canopy and faster drying',
      'Time irrigation to avoid long wetting of leaves',
    ],
    management: [
      'Follow regional spray calendars from horticulture departments',
      'Use only registered fungicides at label timings — avoid improvising doses',
      'Remove badly infected water shoots when feasible',
      'Monitor fruit clusters after bloom',
    ],
    whenToAct:
      'Start monitoring at green tip / bloom in spring. Act quickly after infection periods shown on local scab risk charts or advisor alerts.',
    detectionNotes:
      'Clear leaf photos help FarmEye AI flag possible scab-like patterns; confirm with orchard history and expert scouting.',
    metaDescription:
      'Learn about Apple Scab Lesion, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'cotton-aphid-attack',
    name: 'Cotton Aphid Attack',
    crop: 'Cotton',
    category: 'Pest',
    image:
      'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-5',
    shortDescription: 'Tiny sap-sucking insects on cotton that curl leaves and leave sticky honeydew.',
    overview:
      'Cotton aphids feed on leaf undersides, causing curling, stunting, and sticky honeydew. Heavy infestations may invite sooty mould and virus spread. General pest information for farmers.',
    symptoms: [
      'Clusters of small green or yellow insects under leaves',
      'Curled or twisted young leaves and shoots',
      'Shiny sticky honeydew on leaves or bolls',
      'Sooty black mould on honeydew-coated areas',
    ],
    causes: [
      'Rapid reproduction in warm, dry weather',
      'Low numbers of natural enemies (ladybirds, lacewings)',
      'Movement from neighbouring infested fields',
      'Excessive nitrogen leading to soft tender growth',
    ],
    favorableConditions: {
      temperature: 'Warm conditions around 25–32°C',
      humidity: 'Lower humidity can favour aphid buildup',
      moisture: 'Irrigated lush growth without predator habitat',
      other: ['Wide-spectrum insecticide use killing beneficial insects', 'Dense cotton stands'],
    },
    severity: 'High',
    severityExplanation:
      'High severity means aphids can multiply quickly, stressing plants and affecting boll development if not managed early.',
    prevention: [
      'Encourage beneficial insects by avoiding unnecessary broad sprays',
      'Monitor borders and nurseries before main season',
      'Use balanced fertilisation',
      'Remove weed hosts near the field edge',
    ],
    management: [
      'Scout undersides of top leaves weekly during squaring and flowering',
      'Use cultural options first: water sprays, pruning heavily infested tips where practical',
      'Choose biocontrol or soft pesticides per local cotton IPM guidelines and labels',
      'Rotate control methods to reduce resistance — follow agriculture department advice',
    ],
    whenToAct:
      'Take action when colonies appear on many plants or honeydew is visible before peak flowering. Seek IPM advice for threshold counts in your area.',
    detectionNotes:
      'FarmEye AI may help spot leaf curling and pest-like clusters in images; field counts of aphids per leaf are still essential.',
    metaDescription:
      'Learn about Cotton Aphid Attack, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'rice-blast-disease',
    name: 'Rice Blast Disease',
    crop: 'Rice',
    category: 'Disease',
    image:
      'https://images.unsplash.com/photo-1536657464919-892534f60d6e?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-6',
    shortDescription: 'Diamond-shaped gray-centred spots on rice leaves during humid, rainy spells.',
    overview:
      'Rice blast is a major fungal disease causing spindle-shaped lesions on leaves and necks. It spreads in humid paddy conditions. This page provides general guidance, not a confirmed blast report.',
    symptoms: [
      'Eye-shaped or diamond lesions with gray centres and brown borders',
      'Leaf wilting or drying from tip downward in severe cases',
      'Neck rot causing panicles to fall (neck blast) at heading',
      'Lesions on leaf collars and nodes in advanced stages',
    ],
    causes: [
      'Fungal spores spread by wind and rain within and between fields',
      'Excessive nitrogen fertilisation',
      'Dense planting and shade in the lower canopy',
    ],
    favorableConditions: {
      temperature: 'Warm, humid periods around 25–28°C',
      humidity: 'Very high humidity, often above 85%',
      moisture: 'Continuous leaf wetness from rain or deep standing water splashing',
      other: ['Heavy nitrogen top-dressing', 'Susceptible varieties', 'Cloudy weather for several days'],
    },
    severity: 'High',
    severityExplanation:
      'High severity reflects blast’s ability to damage leaves and panicles quickly in favourable weather, with significant yield loss if unchecked.',
    prevention: [
      'Use blast-tolerant varieties recommended for your agro-climatic zone',
      'Split nitrogen applications instead of single heavy doses',
      'Maintain recommended plant spacing and water depth',
      'Avoid introducing infected seedlings',
    ],
    management: [
      'Drain fields briefly if standing water is excessive (per local water management advice)',
      'Apply fungicides only as per state rice IPM schedules and labels',
      'Remove severely infected patches to reduce spore load where feasible',
      'Monitor neck blast risk at heading',
    ],
    whenToAct:
      'Inspect after prolonged cloudy, rainy weather. Report to extension services if lesions appear on the flag leaf or neck region.',
    detectionNotes:
      'Upload clear rice leaf images to FarmEye AI for symptom hints; laboratory confirmation may be needed for breeding or export plots.',
    metaDescription:
      'Learn about Rice Blast Disease, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
  {
    id: 'wheat-septoria-leaf-blotch',
    name: 'Wheat Septoria Leaf Blotch',
    crop: 'Wheat',
    category: 'Disease',
    image:
      'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1200&q=80',
    sampleId: 'sample-7',
    shortDescription: 'Rectangular brown blotches on wheat leaves, often with tiny black specks.',
    overview:
      'Septoria leaf blotch causes elongated brown lesions on wheat leaves, usually starting on lower foliage. It can reduce grain fill if it reaches the upper leaves early. Educational reference only.',
    symptoms: [
      'Rectangular brown lesions between leaf veins',
      'Tiny black fruiting bodies (specks) within lesions',
      'Yellowing and death of lower leaves first',
      'Premature senescence under heavy infection',
    ],
    causes: [
      'Fungal spores from infected stubble and volunteer wheat',
      'Rain splash moving spores up the plant',
      'Continuous wheat or wheat-on-wheat rotations',
    ],
    favorableConditions: {
      temperature: 'Mild temperatures around 15–22°C',
      humidity: 'Frequent light rains and high humidity',
      moisture: 'Leaf wetness for many hours after rain or fog',
      other: ['Early sowing into retained stubble', 'Dense stands with poor airflow'],
    },
    severity: 'Moderate',
    severityExplanation:
      'Moderate severity means early lower-leaf infection is common, but yield impact depends on how soon lesions reach the flag leaf before grain fill.',
    prevention: [
      'Rotate wheat with non-host crops',
      'Manage stubble according to local conservation guidelines',
      'Use certified seed and resistant varieties where available',
      'Avoid excessive early nitrogen',
    ],
    management: [
      'Scout lower canopy at tillering and stem elongation',
      'Consider fungicide timing based on local septoria models or advisor guidance — follow label directions',
      'Improve drainage in waterlogged patches',
      'Record severity each season to plan rotations',
    ],
    whenToAct:
      'Check fields 7–10 days after rainy spells. Seek advice if blotches move to the top two leaves before flowering.',
    detectionNotes:
      'FarmEye AI can help document septoria-like lesions from photos; combine with field scouting across the plot.',
    metaDescription:
      'Learn about Wheat Septoria Leaf Blotch, its symptoms, causes, prevention, and how FarmEye AI can assist with crop-image analysis.',
  },
];

export function getDiseaseBySlug(slug: string): DiseaseLibraryEntry | undefined {
  return DISEASE_LIBRARY.find((entry) => entry.id === slug);
}

export function getDiseaseBySampleId(sampleId: string): DiseaseLibraryEntry | undefined {
  return DISEASE_LIBRARY.find((entry) => entry.sampleId === sampleId);
}
