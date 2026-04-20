/**
 * Constraint Flow — Exact arithmetic workflows
 */

export interface WorkflowStep {
  name: string;
  operation: 'add' | 'multiply' | 'divide' | 'sqrt';
  inputs: number[];
}

export class ExactWorkflow {
  private steps: WorkflowStep[] = [];
  private results: Map<string, number> = new Map();

  addStep(step: WorkflowStep): void {
    this.steps.push(step);
  }

  execute(): number[] {
    return this.steps.map(step => {
      let result: number;
      switch (step.operation) {
        case 'add': result = step.inputs.reduce((a, b) => a + b, 0); break;
        case 'multiply': result = step.inputs.reduce((a, b) => a * b, 1); break;
        case 'divide': result = step.inputs[0] / step.inputs[1]; break;
        case 'sqrt': result = Math.sqrt(step.inputs[0]); break;
        default: result = 0;
      }
      this.results.set(step.name, result);
      return result;
    });
  }

  getResult(name: string): number | undefined {
    return this.results.get(name);
  }
}
