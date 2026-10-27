import {epicScenes,epicV11} from './hk-v11';
export const epicV12={...epicV11,composition:'BOI-HK-Epic-v12-Stage1',mix:'music/v12/review-mix.wav'} as const;
export const epicScenesV12=epicScenes.map(s=>({...s}));
export type EpicSceneV12Id=typeof epicScenesV12[number]['id'];
