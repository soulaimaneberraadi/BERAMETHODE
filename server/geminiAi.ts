/**
 * Gemini calls — server-side only (API key from process.env, never sent to the browser).
 */
import { GoogleGenAI, Type } from '@google/genai';
import type { Machine, Operation } from '../types';

function getGeminiApiKey(): string | undefined {
  const k = process.env.GEMINI_API_KEY?.trim() || process.env.API_KEY?.trim();
  return k || undefined;
}

const operationSchema = {
  type: Type.ARRAY,
  items: {
    type: Type.OBJECT,
    properties: {
      order: { type: Type.NUMBER, description: 'Numéro de séquence logique' },
      description: { type: Type.STRING, description: 'Description technique précise' },
      machineName: { type: Type.STRING, description: 'Nom exact de la machine' },
      length: { type: Type.NUMBER, description: 'Longueur de la couture en CM' },
      stitchCount: { type: Type.NUMBER, description: 'Densité de points (pts/cm)' },
      manualTime: { type: Type.NUMBER, description: 'Temps de manipulation manuel (en cmin)' },
    },
    required: ['order', 'description', 'machineName', 'length', 'stitchCount', 'manualTime'],
  },
};

export async function analyzeTextileContextServer(
  currentOperations: Operation[],
  availableMachines: Machine[],
  userPrompt: string
): Promise<string> {
  const apiKey = getGeminiApiKey();
  if (!apiKey) throw new Error('GEMINI_API_KEY non configurée sur le serveur');

  const client = new GoogleGenAI({ apiKey });
  const machinesList = availableMachines.map((m) => m.name).join(', ');
  const operationsText =
    currentOperations.length > 0
      ? currentOperations
          .map((op) => `${op.order}. ${op.description} [${op.machineName || 'MAN'}] (${op.time.toFixed(2)} min)`)
          .join('\n')
      : 'Aucune opération saisie pour le moment.';

  const response = await client.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: `Tu es un Expert Méthode Textile (GSD).
      
      CONTEXTE - L'UTILISATEUR A SAISI CETTE GAMME MANUELLEMENT :
      ${operationsText}
      
      TA MISSION :
      1. "Lire" et "Comprendre" la gamme ci-dessus.
      2. Répondre à la demande de l'utilisateur : "${userPrompt}".
      3. Si l'utilisateur demande une analyse, identifie le type de vêtement, critique l'équilibrage ou suggère des améliorations.
      4. Si la gamme est vide, propose de l'aide pour commencer.

      Ton ton doit être professionnel, encourageant et technique. Tu es l'assistant, pas le créateur.`,
    config: { temperature: 0.3 },
  });

  const text = response.text;
  if (!text) throw new Error('Réponse vide de l\'IA');
  return text;
}

export async function suggestTextileVocabularyServer(
  contextText: string,
  existingVocabulary: string[] = [],
  limit: number = 10
): Promise<string[]> {
  const apiKey = getGeminiApiKey();
  if (!apiKey) return [];

  const client = new GoogleGenAI({ apiKey });
  const safeLimit = Math.max(3, Math.min(20, Math.floor(limit)));
  const existingSample = existingVocabulary.filter(Boolean).slice(0, 120).join(', ');

  const response = await client.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: `Tu es expert methode textile.
Propose ${safeLimit} mots techniques utiles pour une gamme de confection textile.
Contraines:
- Reponse en FR, termes courts, pratiques atelier.
- IMPORTANT: un seul mot par element (pas d'expression, pas de phrase, pas d'espace).
- Eviter les doublons exacts.
- Eviter les termes deja presents si possible.
- Retourne UNIQUEMENT un JSON array de strings.

Contexte saisie utilisateur:
${contextText}

Vocabulaire existant (a eviter):
${existingSample || 'Aucun'}`,
    config: {
      temperature: 0.25,
      responseMimeType: 'application/json',
      responseSchema: {
        type: Type.ARRAY,
        items: { type: Type.STRING },
      },
    },
  });

  const text = response.text;
  if (!text) return [];
  const parsed = JSON.parse(text);
  if (!Array.isArray(parsed)) return [];

  const seen = new Set<string>();
  const existingLower = new Set(existingVocabulary.map((v) => (v || '').toLowerCase()));

  return parsed
    .map((v: unknown) => (typeof v === 'string' ? v.trim() : ''))
    .filter((v: string) => v.length >= 4)
    .filter((v: string) => !/\s/.test(v))
    .filter((v: string) => /^[A-Za-zÀ-ÿ0-9'-]+$/.test(v))
    .filter((v: string) => {
      const key = v.toLowerCase();
      if (seen.has(key) || existingLower.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, safeLimit);
}

/** Legacy / optional — kept for API completeness */
export async function generateTextileOperationsServer(articleDescription: string, availableMachines: Machine[]) {
  const apiKey = getGeminiApiKey();
  if (!apiKey) throw new Error('GEMINI_API_KEY non configurée sur le serveur');

  const client = new GoogleGenAI({ apiKey });
  const machinesContext = availableMachines
    .filter((m) => m.active)
    .map((m) => `- ${m.name} (Code: ${m.classe}, Vitesse: ${m.speed} tr/min)`)
    .join('\n');

  const response = await client.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: `Rôle : Expert Méthode & Industrialisation Textile (GSD).
      CONTEXTE MACHINES : ${machinesContext}
      MISSION : Générer la Gamme de Montage pour : "${articleDescription}".
      Retourne le JSON strict.`,
    config: {
      responseMimeType: 'application/json',
      responseSchema: operationSchema,
      temperature: 0.1,
    },
  });

  const text = response.text;
  if (!text) throw new Error('Réponse vide de l\'IA');
  return JSON.parse(text);
}
