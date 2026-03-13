import { IsNotEmpty, IsString, MaxLength } from 'class-validator';

export class CreateCandidateDocumentDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  documentType!: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  fileName!: string;

  @IsString()
  @IsNotEmpty()
  rawText!: string;
}
