/**
 * Constraint Ranch — Multi-agent puzzle game
 * 
 * Agents collaborate to solve constraint puzzles.
 */

export interface Agent {
  id: string;
  role: 'planner' | 'solver' | 'validator';
  constraints: Constraint[];
}

export interface Constraint {
  type: 'exact' | 'range' | 'exclusion';
  value: number | string | [number, number];
}

export class Ranch {
  private agents: Agent[] = [];
  private solvedPuzzles = 0;

  addAgent(agent: Agent): void {
    this.agents.push(agent);
  }

  solve(puzzle: Constraint[]): boolean {
    // Simplified solving logic
    const validators = this.agents.filter(a => a.role === 'validator');
    const allValid = validators.every(v => 
      v.constraints.every(c => this.checkConstraint(c, puzzle))
    );
    if (allValid) this.solvedPuzzles++;
    return allValid;
  }

  private checkConstraint(constraint: Constraint, puzzle: Constraint[]): boolean {
    return puzzle.some(p => p.type === constraint.type);
  }

  getStats(): { agents: number; solved: number } {
    return { agents: this.agents.length, solved: this.solvedPuzzles };
  }
}

export { Ranch as default };
