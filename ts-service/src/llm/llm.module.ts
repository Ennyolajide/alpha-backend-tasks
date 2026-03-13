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
        const useFake = configService.get<string>('USE_FAKE_LLM') === 'true';
        return useFake ? fake : gemini;
      },
      inject: [ConfigService, GeminiSummarizationProvider, FakeSummarizationProvider],
    },
  ],
  exports: [SUMMARIZATION_PROVIDER, FakeSummarizationProvider, GeminiSummarizationProvider],
})
export class LlmModule {}
