/**
 * @license
 * Copyright 2018 Google LLC
 *
 * Use of this source code is governed by an MIT-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/MIT.
 * =============================================================================
 */

/* Unit tests for constraints */

// tslint:disable:max-line-length
import {Tensor1D, tensor1d} from 'deeplearn';

import {deserialize, get, MinMaxNorm, MinMaxNormConfig, NonNeg, serialize} from './constraints';
import {ConfigDict} from './types';
import {describeMathCPU, expectTensorsClose} from './utils/test_utils';
// tslint:enable:max-line-length

describeMathCPU('Built-in Constraints', () => {
  let initVals: Tensor1D;
  beforeEach(() => {
    initVals = tensor1d(new Float32Array([-1, 2, 0, 4, -5, 6]));
  });

  it('NonNeg', () => {
    const constraint = get('NonNeg');
    const postConstraint = constraint.apply(initVals);
    expectTensorsClose(
        postConstraint, tensor1d(new Float32Array([0, 2, 0, 4, 0, 6])));
  });
  it('MaxNorm', () => {
    const constraint = get('MaxNorm');
    const postConstraint = constraint.apply(initVals);
    expectTensorsClose(postConstraint, tensor1d(new Float32Array([
                         -0.2208630521, 0.4417261043, 0, 0.8834522086,
                         -1.104315261, 1.325178313
                       ])));
  });
  it('UnitNorm', () => {
    const constraint = get('UnitNorm');
    const postConstraint = constraint.apply(initVals);
    expectTensorsClose(postConstraint, tensor1d(new Float32Array([
                         -0.2208630521 / 2, 0.4417261043 / 2, 0,
                         0.8834522086 / 2, -1.104315261 / 2, 1.325178313 / 2
                       ])));
  });
  it('MinMaxNorm', () => {
    const constraint = get('MinMaxNorm');
    const postConstraint = constraint.apply(initVals);
    expectTensorsClose(postConstraint, tensor1d(new Float32Array([
                         -0.2208630521 / 2, 0.4417261043 / 2, 0,
                         0.8834522086 / 2, -1.104315261 / 2, 1.325178313 / 2
                       ])));
  });
});

describeMathCPU('constraints.get', () => {
  it('by string', () => {
    const constraint = get('MaxNorm');
    const config = serialize(constraint) as ConfigDict;
    const nestedConfig = config.config as ConfigDict;
    expect(nestedConfig.maxValue).toEqual(2);
    expect(nestedConfig.axis).toEqual(0);
  });
  it('by existing object', () => {
    const origConstraint = new NonNeg();
    expect(get(origConstraint)).toEqual(origConstraint);
  });
  it('by config dict', () => {
    const config:
        MinMaxNormConfig = {minValue: 0, maxValue: 2, rate: 3, axis: 4};
    const origConstraint = new MinMaxNorm(config);
    const constraint = get(serialize(origConstraint) as ConfigDict);
    expect(serialize(constraint)).toEqual(serialize(origConstraint));
  });
});

describe('Constraints Serialization', () => {
  it('Built-ins', () => {
    for (const name of ['MaxNorm', 'NonNeg', 'UnitNorm', 'MinMaxNorm']) {
      const constraint = get(name);
      const config = serialize(constraint) as ConfigDict;
      const reconstituted = deserialize(config);
      expect(reconstituted).toEqual(constraint);
    }
  });
});
