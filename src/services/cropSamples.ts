import type { SampleCropImage } from '../types/crop';

export const SAMPLE_CROP_IMAGES: SampleCropImage[] = [
  {
    id: 'sample-1',
    name: 'Tomato Leaf Blight',
    cropType: 'tomato',
    description: 'Tomato leaf displaying irregular dark water-soaked lesions with halo',
    imageUrl: '/assets/tomato_late_blight.jpg',
    mockResult: {
      id: 'res-tomato-blight',
      timestamp: new Date().toISOString(),
      imageUrl: '/assets/tomato_late_blight.jpg',
      cropType: 'tomato',
      growthStage: 'fruiting',
      location: 'Plot 4B - Greenhouse Alpha',
      diagnosis: {
        diseaseName: 'Tomato Late Blight',
        scientificName: 'Phytophthora infestans',
        confidence: 94.8,
        isReliable: true,
        severity: 'moderate',
        summary: 'Detected active oomycete fungal infection characterized by dark necrotizing leaf lesions and light margin halo. Spores propagate rapidly in high humidity.',
        boundingBoxes: [
          { id: 'bb1', label: 'Necrotic Lesion', confidence: 96, x: 22, y: 28, width: 26, height: 32, type: 'lesion' },
          { id: 'bb2', label: 'Secondary Spore Lesion', confidence: 91, x: 58, y: 44, width: 22, height: 24, type: 'lesion' },
          { id: 'bb3', label: 'Margin Chlorosis', confidence: 88, x: 18, y: 22, width: 34, height: 42, type: 'symptom' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: [],
        notes: 'No insect pest vectors (aphids/thrips) observed on tomato leaf surface.'
      },
      environment: {
        temperature: 21.5,
        humidity: 88,
        rainfall: 14.2,
        leafWetnessHours: 9.5,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'high',
        contributingFactors: [
          'Relative humidity > 85% sustained for 9+ hours',
          'Cool ambient temperature (21.5°C) optimal for Phytophthora sporulation',
          'Recent rainfall creating dense canopy leaf wetness'
        ],
        isDataSufficient: true,
        explanation: 'Microclimate metrics strongly support rapid spore dissemination across adjacent tomato rows.'
      },
      recommendations: [
        {
          id: 'rec-1',
          category: 'monitor',
          title: 'Daily Canopy Inspection',
          description: 'Inspect undersides of tomato leaves in surrounding 5-meter radius twice daily.',
          urgency: 'high'
        },
        {
          id: 'rec-2',
          category: 'field_care',
          title: 'Targeted Fungicide Spraying',
          description: 'Apply copper hydroxide or chlorothalonil systemic fungicide within 24 hours to contain spreading.',
          urgency: 'high'
        },
        {
          id: 'rec-3',
          category: 'field_care',
          title: 'Prune Lower Infected Leaves',
          description: 'Remove heavily necrotic bottom foliage and destroy off-field. Do not compost infected leaves.',
          urgency: 'medium'
        },
        {
          id: 'rec-4',
          category: 'follow_up',
          title: 'Improve Row Ventilation',
          description: 'Increase air circulation by thinning non-bearing vegetative lateral shoots.',
          urgency: 'medium'
        }
      ],
      alerts: [
        {
          id: 'alt-1',
          severity: 'critical',
          reason: 'Late Blight active in Tomato Plot 4B with high humidity forecast.',
          timestamp: 'Just now',
          action: 'Apply protective copper fungicide immediately.',
          cropType: 'Tomato'
        }
      ]
    }
  },
  {
    id: 'sample-2',
    name: 'Potato Early Blight',
    cropType: 'potato',
    description: 'Potato crop foliage displaying target-board concentric spot rings',
    imageUrl: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-potato-blight',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1200&q=80',
      cropType: 'potato',
      growthStage: 'vegetative',
      location: 'East Valley Field 7',
      diagnosis: {
        diseaseName: 'Potato Early Blight',
        scientificName: 'Alternaria solani',
        confidence: 89.5,
        isReliable: true,
        severity: 'mild',
        summary: 'Target-board concentric rings identified on lower older potato leaves, indicating early Alternaria spot formation.',
        boundingBoxes: [
          { id: 'bb-p1', label: 'Concentric Ring Lesion', confidence: 90, x: 40, y: 35, width: 24, height: 26, type: 'lesion' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: [],
        notes: 'No Colorado potato beetle larvae observed.'
      },
      environment: {
        temperature: 24.2,
        humidity: 68,
        rainfall: 0,
        leafWetnessHours: 4.5,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'moderate',
        contributingFactors: [
          'Alternaria fungal spores persist in crop debris',
          'Heavy morning dew creates favorable sporulation window'
        ],
        isDataSufficient: true,
        explanation: 'Infection is currently localized to lower potato leaves.'
      },
      recommendations: [
        {
          id: 'rec-pot-1',
          category: 'monitor',
          title: 'Scout Lower Leaves Weekly',
          description: 'Inspect lower canopy of potato plants for expanding concentric brown spots.',
          urgency: 'medium'
        },
        {
          id: 'rec-pot-2',
          category: 'field_care',
          title: 'Foliar Protectant Fungicide',
          description: 'Apply mancozeb protectant fungicide to maintain foliage health before flowering.',
          urgency: 'medium'
        }
      ],
      alerts: [
        {
          id: 'alt-pot-1',
          severity: 'warning',
          reason: 'Early Blight detected in Potato Field 7.',
          timestamp: '1 hour ago',
          action: 'Apply protectant spray.',
          cropType: 'Potato'
        }
      ]
    }
  },
  {
    id: 'sample-3',
    name: 'Corn Leaf Rust',
    cropType: 'corn',
    description: 'Corn foliage displaying classic raised golden-brown pustules',
    imageUrl: 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-corn-rust',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1200&q=80',
      cropType: 'corn',
      growthStage: 'vegetative',
      location: 'North Field Block C',
      diagnosis: {
        diseaseName: 'Corn Common Rust',
        scientificName: 'Puccinia sorghi',
        confidence: 91.2,
        isReliable: true,
        severity: 'mild',
        summary: 'Small, circular pustules of cinnamon-brown urediniospores identified on upper corn leaf surface.',
        boundingBoxes: [
          { id: 'bb-c1', label: 'Rust Pustule Cluster', confidence: 93, x: 35, y: 30, width: 30, height: 25, type: 'lesion' },
          { id: 'bb-c2', label: 'Spore Pustule', confidence: 89, x: 20, y: 60, width: 18, height: 18, type: 'lesion' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: [],
        notes: 'No corn borer or armyworm pest activity detected.'
      },
      environment: {
        temperature: 24.0,
        humidity: 72,
        rainfall: 2.1,
        leafWetnessHours: 5.0,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'moderate',
        contributingFactors: [
          'Warm dew-heavy mornings favor spore germination',
          'Crop stage (vegetative V8) retains moderate yield resistance'
        ],
        isDataSufficient: true,
        explanation: 'Infection is currently early-stage. Monitor weather over the coming 3 days.'
      },
      recommendations: [
        {
          id: 'rec-c1',
          category: 'monitor',
          title: 'Track Pustule Density',
          description: 'Check 20 random corn stalks across Block C to determine if >5% leaf area is affected.',
          urgency: 'medium'
        },
        {
          id: 'rec-c2',
          category: 'field_care',
          title: 'Foliar Fungicide (Conditional)',
          description: 'Fungicide treatment is only required if infection spreads above ear leaf before tasseling.',
          urgency: 'low'
        }
      ],
      alerts: [
        {
          id: 'alt-c1',
          severity: 'warning',
          reason: 'Common Rust detected in early vegetative corn.',
          timestamp: '1 hour ago',
          action: 'Monitor upper leaf canopy weekly.',
          cropType: 'Corn'
        }
      ]
    }
  },
  {
    id: 'sample-4',
    name: 'Apple Scab Lesion',
    cropType: 'apple',
    description: 'Apple foliage displaying olive-green velvety lesion spots',
    imageUrl: 'https://images.unsplash.com/photo-1567306301408-9b74779a11af?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-apple-scab',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1567306301408-9b74779a11af?auto=format&fit=crop&w=1200&q=80',
      cropType: 'apple',
      growthStage: 'fruiting',
      location: 'Orchard Sector 2',
      diagnosis: {
        diseaseName: 'Apple Scab',
        scientificName: 'Venturia inaequalis',
        confidence: 93.4,
        isReliable: true,
        severity: 'moderate',
        summary: 'Olive-brown velvety leaf spots with feathery margins identified on upper apple leaf blade.',
        boundingBoxes: [
          { id: 'bb-a1', label: 'Velvety Scab Lesion', confidence: 94, x: 25, y: 30, width: 35, height: 35, type: 'lesion' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: [],
        notes: 'Pest inspection negative. No red mite webbing detected on apple leaf.'
      },
      environment: {
        temperature: 18.8,
        humidity: 82,
        rainfall: 8.4,
        leafWetnessHours: 8.0,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'high',
        contributingFactors: [
          'Sustained canopy wetness duration > 8 hours',
          'Spring rainfall accelerates ascospore discharge from orchard floor'
        ],
        isDataSufficient: true,
        explanation: 'Primary infection period active. Secondary spread threatens fruit set.'
      },
      recommendations: [
        {
          id: 'rec-app-1',
          category: 'field_care',
          title: 'Apply Post-Infection Myclobutanil',
          description: 'Spray systemic fungicide with curative kickback action within 48h of rain event.',
          urgency: 'high'
        },
        {
          id: 'rec-app-2',
          category: 'monitor',
          title: 'Scout Developing Fruit Clusters',
          description: 'Inspect young apple fruitlets for dark corky skin spots.',
          urgency: 'medium'
        }
      ],
      alerts: [
        {
          id: 'alt-app-1',
          severity: 'critical',
          reason: 'Apple Scab primary ascospore risk high in Sector 2.',
          timestamp: '45 mins ago',
          action: 'Spray systemic protectant fungicide.',
          cropType: 'Apple'
        }
      ]
    }
  },
  {
    id: 'sample-5',
    name: 'Cotton Aphid Attack',
    cropType: 'cotton',
    description: 'Cotton leaf undersides infested with aphid colonies causing leaf curl',
    imageUrl: 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-cotton-aphid',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80',
      cropType: 'cotton',
      growthStage: 'flowering',
      location: 'South Field Row 12',
      diagnosis: {
        diseaseName: 'Secondary Sooty Mold (Aphid Induced)',
        scientificName: 'Capnodium spp.',
        confidence: 86.4,
        isReliable: true,
        severity: 'moderate',
        summary: 'Cotton leaf curling and honeydew deposits identified, resulting from active sucking insect pest colony.',
        boundingBoxes: [
          { id: 'bb-a1', label: 'Leaf Distortion', confidence: 88, x: 15, y: 20, width: 45, height: 40, type: 'symptom' }
        ]
      },
      pests: {
        detected: true,
        pestName: 'Cotton Aphid (Aphis gossypii)',
        pestCount: 42,
        confidence: 96.5,
        boundingBoxes: [
          { id: 'bb-p1', label: 'Aphid Colony Cluster', confidence: 97, x: 28, y: 32, width: 28, height: 28, type: 'pest' },
          { id: 'bb-p2', label: 'Aphid Vector', confidence: 94, x: 60, y: 50, width: 18, height: 16, type: 'pest' }
        ],
        notes: 'Dense aphid nymphs feeding on phloem sap, producing sticky honeydew excretions.'
      },
      environment: {
        temperature: 29.8,
        humidity: 60,
        rainfall: 0,
        leafWetnessHours: 1.2,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'high',
        contributingFactors: [
          'High ambient temperature (29.8°C) accelerates aphid breeding cycles',
          'Low natural predator count (ladybugs/lacewings) observed'
        ],
        isDataSufficient: true,
        explanation: 'Rapid pest proliferation threatens honeydew contamination on developing cotton bolls.'
      },
      recommendations: [
        {
          id: 'rec-p1',
          category: 'field_care',
          title: 'Introduce Beneficial Predators',
          description: 'Release ladybird beetle larvae (Hippodamia convergens) as biological pest control.',
          urgency: 'high'
        },
        {
          id: 'rec-p2',
          category: 'field_care',
          title: 'Insecticidal Soap Spray',
          description: 'Apply potassium salts of fatty acids or neem oil extract under cotton leaf surface.',
          urgency: 'high'
        }
      ],
      alerts: [
        {
          id: 'alt-p1',
          severity: 'critical',
          reason: 'High density Aphid infestation detected in Cotton (42 count/leaf).',
          timestamp: '30 mins ago',
          action: 'Apply organic neem/insecticidal soap immediately.',
          cropType: 'Cotton'
        }
      ]
    }
  },
  {
    id: 'sample-6',
    name: 'Rice Blast Disease',
    cropType: 'rice',
    description: 'Rice leaf blades displaying eye-shaped spindle lesions with gray centers',
    imageUrl: 'https://images.unsplash.com/photo-1536657464919-892534f60d6e?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-rice-blast',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1536657464919-892534f60d6e?auto=format&fit=crop&w=1200&q=80',
      cropType: 'rice',
      growthStage: 'vegetative',
      location: 'Paddy Field Block 3',
      diagnosis: {
        diseaseName: 'Rice Blast',
        scientificName: 'Magnaporthe oryzae',
        confidence: 92.7,
        isReliable: true,
        severity: 'moderate',
        summary: 'Diamond/spindle-shaped leaf lesions with reddish-brown borders and grayish necrotic centers detected on rice foliage.',
        boundingBoxes: [
          { id: 'bb-r1', label: 'Spindle Blast Lesion', confidence: 93, x: 30, y: 25, width: 30, height: 35, type: 'lesion' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: [],
        notes: 'No brown planthopper or stem borer activity detected.'
      },
      environment: {
        temperature: 27.5,
        humidity: 90,
        rainfall: 25.0,
        leafWetnessHours: 11.0,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'high',
        contributingFactors: [
          'High relative humidity (>88%) and excessive nitrogen fertilization',
          'Prolonged leaf wetness duration (>10 hours)'
        ],
        isDataSufficient: true,
        explanation: 'Favorable condition for rapid conidial sporulation across paddy canopy.'
      },
      recommendations: [
        {
          id: 'rec-r1',
          category: 'field_care',
          title: 'Apply Tricyclazole Fungicide',
          description: 'Spray tricyclazole or isoprothiolane at first sign of leaf blast lesions.',
          urgency: 'high'
        },
        {
          id: 'rec-r2',
          category: 'field_care',
          title: 'Regulate Nitrogen Water Level',
          description: 'Avoid excessive top-dressing of nitrogenous fertilizer and maintain 5cm water depth.',
          urgency: 'medium'
        }
      ],
      alerts: [
        {
          id: 'alt-r1',
          severity: 'critical',
          reason: 'Rice Blast active in Paddy Block 3.',
          timestamp: '15 mins ago',
          action: 'Apply tricyclazole spray immediately.',
          cropType: 'Rice'
        }
      ]
    }
  },
  {
    id: 'sample-7',
    name: 'Wheat Septoria Leaf Blotch',
    cropType: 'wheat',
    description: 'Wheat leaf blades displaying rectangular brown lesions with black pycnidia specks',
    imageUrl: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1200&q=80',
    mockResult: {
      id: 'res-wheat-septoria',
      timestamp: new Date().toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1200&q=80',
      cropType: 'wheat',
      growthStage: 'vegetative',
      location: 'Plot 9 - Research Farm',
      diagnosis: {
        diseaseName: 'Wheat Septoria Leaf Blotch',
        scientificName: 'Zymoseptoria tritici',
        confidence: 88.6,
        isReliable: true,
        severity: 'mild',
        summary: 'Elongated rectangular yellow-brown lesions containing visible tiny black fruiting bodies (pycnidia) on wheat foliage.',
        boundingBoxes: [
          { id: 'bb-w1', label: 'Septoria Lesion', confidence: 89, x: 25, y: 35, width: 40, height: 25, type: 'lesion' }
        ]
      },
      pests: {
        detected: false,
        boundingBoxes: []
      },
      environment: {
        temperature: 16.5,
        humidity: 78,
        rainfall: 5.2,
        leafWetnessHours: 7.0,
        isDataSufficient: true
      },
      risk: {
        riskLevel: 'moderate',
        contributingFactors: ['Cool wet conditions favor rain-splash spore dispersal up canopy'],
        isDataSufficient: true,
        explanation: 'Fungus spreading from lower leaves towards upper flag leaf.'
      },
      recommendations: [
        {
          id: 'rec-w1',
          category: 'field_care',
          title: 'Protect Flag Leaf (T2 Timing)',
          description: 'Apply SDHI or azole fungicide before flag leaf emergence to safeguard yield.',
          urgency: 'high'
        }
      ],
      alerts: [
        {
          id: 'alt-w1',
          severity: 'warning',
          reason: 'Septoria Leaf Blotch detected in Wheat Plot 9.',
          timestamp: '2 hours ago',
          action: 'Plan T2 fungicide application.',
          cropType: 'Wheat'
        }
      ]
    }
  }
];
