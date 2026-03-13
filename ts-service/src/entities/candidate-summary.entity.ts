import {
  Column,
  CreateDateColumn,
  Entity,
  JoinColumn,
  ManyToOne,
  PrimaryColumn,
  UpdateDateColumn,
} from 'typeorm';

import { SampleCandidate } from './sample-candidate.entity';
import { SampleWorkspace } from './sample-workspace.entity';

@Entity({ name: 'candidate_summaries' })
export class CandidateSummary {
  @PrimaryColumn({ type: 'varchar', length: 64 })
  id!: string;

  @Column({ name: 'candidate_id', type: 'varchar', length: 64 })
  candidateId!: string;

  @Column({ name: 'workspace_id', type: 'varchar', length: 64 })
  workspaceId!: string;

  @Column({ type: 'varchar', length: 20, default: 'pending' })
  status!: 'pending' | 'completed' | 'failed';

  @Column({ type: 'int', nullable: true })
  score!: number | null;

  @Column({ type: 'simple-array', nullable: true })
  strengths!: string[] | null;

  @Column({ type: 'simple-array', nullable: true })
  concerns!: string[] | null;

  @Column({ type: 'text', nullable: true })
  summary!: string | null;

  @Column({ name: 'recommended_decision', type: 'varchar', length: 50, nullable: true })
  recommendedDecision!: string | null;

  @Column({ type: 'varchar', length: 100, nullable: true })
  provider!: string | null;

  @Column({ name: 'prompt_version', type: 'varchar', length: 50, nullable: true })
  promptVersion!: string | null;

  @Column({ name: 'error_message', type: 'text', nullable: true })
  errorMessage!: string | null;

  @CreateDateColumn({ name: 'created_at', type: 'timestamptz' })
  createdAt!: Date;

  @UpdateDateColumn({ name: 'updated_at', type: 'timestamptz' })
  updatedAt!: Date;

  @ManyToOne(() => SampleCandidate, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'candidate_id' })
  candidate!: SampleCandidate;

  @ManyToOne(() => SampleWorkspace, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'workspace_id' })
  workspace!: SampleWorkspace;
}
