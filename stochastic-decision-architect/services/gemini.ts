import { GoogleGenAI } from "@google/genai";
import { Criterion, Evaluation, Option, GroundingSource } from "../types";

const getAiClient = () => {
  const apiKey = process.env.API_KEY;
  if (!apiKey) throw new Error("API_KEY not found in environment");
  return new GoogleGenAI({ apiKey });
};

/**
 * Step 1: Analyze topic, perform Google Search, and suggest Options/Criteria.
 */
export const analyzeTopicAndSuggest = async (
  topic: string,
  userContext: string
): Promise<{ options: Option[]; criteria: Criterion[]; sources: GroundingSource[] }> => {
  const ai = getAiClient();

  const prompt = `
    The user wants to make a decision about: "${topic}".
    Context: "${userContext}".

    1. Use Google Search to find real-world, up-to-date options and relevant criteria for this decision.
    2. Identify at least 3 distinct, viable options.
    3. Identify 4-6 key criteria for evaluating these options (e.g., cost, durability, speed).
    4. Return the result as a raw JSON object (no markdown formatting) with keys: "options" (array with id, name, description) and "criteria" (array with id, name, description, weight). Weight should be 1-10 based on general importance.
  `;

  // Note: responseMimeType/responseSchema is NOT supported with googleSearch
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
    },
  });

  // Extract grounding metadata
  const sources: GroundingSource[] = [];
  const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
  if (chunks) {
    chunks.forEach((chunk: any) => {
      if (chunk.web?.uri && chunk.web?.title) {
        sources.push({ uri: chunk.web.uri, title: chunk.web.title });
      }
    });
  }

  // Parse generic JSON text
  const text = response.text || "{}";
  const cleanedText = text.replace(/```json/g, "").replace(/```/g, "").trim();
  
  try {
    const data = JSON.parse(cleanedText);
    return {
      options: data.options || [],
      criteria: data.criteria || [],
      sources
    };
  } catch (e) {
    console.error("Failed to parse AI response", cleanedText);
    throw new Error("Failed to interpret decision data.");
  }
};

/**
 * Step 2: Evaluate each option against criteria using search data.
 */
export const scoreOptions = async (
  topic: string,
  options: Option[],
  criteria: Criterion[]
): Promise<{ evaluations: Evaluation[]; sources: GroundingSource[] }> => {
  const ai = getAiClient();

  const prompt = `
    I need to evaluate options for the decision: "${topic}".

    Options: ${JSON.stringify(options.map(o => o.name))}
    Criteria: ${JSON.stringify(criteria.map(c => c.name))}

    1. Use Google Search to find specific data points (specs, reviews, prices) to evaluate each option against each criterion.
    2. Score each option on each criterion from 0 to 100.
    3. Provide a short reasoning string for each score.
    4. Return ONLY a raw JSON array of objects with keys: "optionId" (matches option names), "criterionId" (matches criterion names), "score" (number), "reasoning" (string).
    
    IMPORTANT: Map the 'optionId' in the JSON response to the Option Names provided, and 'criterionId' to the Criterion Names provided.
  `;

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
    },
  });

  const sources: GroundingSource[] = [];
  const chunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
  if (chunks) {
    chunks.forEach((chunk: any) => {
      if (chunk.web?.uri && chunk.web?.title) {
        sources.push({ uri: chunk.web.uri, title: chunk.web.title });
      }
    });
  }

  const text = response.text || "[]";
  const cleanedText = text.replace(/```json/g, "").replace(/```/g, "").trim();

  try {
    const rawEvaluations = JSON.parse(cleanedText);
    
    // Map names back to IDs
    const evaluations: Evaluation[] = [];
    
    rawEvaluations.forEach((evalItem: any) => {
      // Fuzzy match or direct name match to find IDs
      const opt = options.find(o => o.name.toLowerCase() === evalItem.optionId.toLowerCase() || o.name === evalItem.optionId);
      const crit = criteria.find(c => c.name.toLowerCase() === evalItem.criterionId.toLowerCase() || c.name === evalItem.criterionId);

      if (opt && crit) {
        evaluations.push({
          optionId: opt.id,
          criterionId: crit.id,
          score: evalItem.score,
          reasoning: evalItem.reasoning
        });
      }
    });

    return { evaluations, sources };

  } catch (e) {
    console.error("Failed to parse scoring response", cleanedText);
    throw new Error("Failed to score options.");
  }
};
