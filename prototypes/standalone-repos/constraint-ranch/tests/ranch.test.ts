import { Ranch, Agent } from '../src/index';

describe('Ranch', () => {
  test('adds agents', () => {
    const ranch = new Ranch();
    ranch.addAgent({ id: '1', role: 'solver', constraints: [] });
    expect(ranch.getStats().agents).toBe(1);
  });
});
