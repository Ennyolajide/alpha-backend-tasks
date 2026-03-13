import { GoogleGenerativeAI } from '@google/generative-ai';
import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

import {
  CandidateSummaryInput,
  CandidateSummaryResult,
  SummarizationProvider,
} from './summarization-provider.interface';

@Injectable()
export class GeminiSummarizationProvider implements SummarizationProvider {
  private readonly logger = new Logger(GeminiSummarizationProvider.name);
  private readonly genAI: GoogleGenerativeAI;

  constructor(private readonly configService: ConfigService) {
    const apiKey = this.configService.get<string>('GEMINI_API_KEY');
    if (!apiKey) {
      this.logger.warn('GEMINI_API_KEY is not set. Summarization will fail.');
    }
    this.genAI = new GoogleGenerativeAI(apiKey || '');
  }

  async generateCandidateSummary(
    input: CandidateSummaryInput,
  ): Promise<CandidateSummaryResult> {
    const model = this.genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

    const prompt = `
      You are an expert recruiter assistant.
      Summarize the following documents for candidate ${input.candidateId}.
      
      Documents:
      ${input.documents.join('\n\n---\n\n')}
      
      Respond only with a JSON object in the following format:
      {
        "score": number (0-100),
        "strengths": string[],
        "concerns": string[],
        "summary": string,
        "recommendedDecision": "advance" | "hold" | "reject"
      }
    `;

    try {
      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      // Clean the response text to extract only the JSON
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('Valid JSON not found in Gemini response');
      }

      const parsed = JSON.parse(jsonMatch[0]);

      return {
        score: parsed.score ?? 0,
        strengths: Array.isArray(parsed.strengths) ? parsed.strengths : [],
        concerns: Array.isArray(parsed.concerns) ? parsed.concerns : [],
        summary: parsed.summary ?? 'No summary provided by model.',
        recommendedDecision: this.validateDecision(parsed.recommendedDecision),
      };
    } catch (error: any) {
      this.logger.error(`Gemini summarization failed: ${error.message}`, error.stack);
      throw error;
    }
  }

  private validateDecision(decision: any): 'advance' | 'hold' | 'reject' {
    const valid = ['advance', 'hold', 'reject'];
    return valid.includes(decision) ? decision : 'hold';
  }
}
