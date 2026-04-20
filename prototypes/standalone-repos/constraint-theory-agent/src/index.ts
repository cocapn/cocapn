/**
 * Constraint Theory Agent — Safe AI agents
 */

export interface SafetyConstraint {
  name: string;
  validate: (output: any) => boolean;
  reason: string;
}

export class SafeAgent {
  private constraints: SafetyConstraint[] = [];
  private name: string;

  constructor(name: string) {
    this.name = name;
  }

  addConstraint(constraint: SafetyConstraint): void {
    this.constraints.push(constraint);
  }

  act(action: any): { safe: boolean; result?: any; reason?: string } {
    for (const constraint of this.constraints) {
      if (!constraint.validate(action)) {
        return { safe: false, reason: constraint.reason };
      }
    }
    return { safe: true, result: action };
  }
}
