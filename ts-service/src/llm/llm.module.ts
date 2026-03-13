import { Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

import { FakeSummarizationProvider } from './fake-summarization.provider';
import { GeminiSummarizationProvider } from './gemini-summarization.provider';
import { SUMMARIZATION_PROVIDER } from './summarization-provider.interface';

@Module({
  providers: [
    FakeSummarizationProvider,
    GeminiSummarizationProvider,
    {
      provide: SUMMARIZATION_PROVIDER,
      useFactory: (
        configService: ConfigService,
        gemini: GeminiSummarizationProvider,
        fake: FakeSummarizationProvider,
      ) => {
        const apiKey = configService.get<string>('GEMINI_API_KEY');
        const useFake = configService.get<string>('USE_FAKE_LLM') === 'true';
        
        // Use fake provider if no API key is provided, or if explicitly set to use fake
        if (!apiKey || apiKey.trim() === '') {
          return fake;
        }
        
        return useFake ? fake : gemini;
      },
      inject: [ConfigService, GeminiSummarizationProvider, FakeSummarizationProvider],
    },
  ],
  exports: [SUMMARIZATION_PROVIDER, FakeSummarizationProvider, GeminiSummarizationProvider],
})
export class LlmModule {}
