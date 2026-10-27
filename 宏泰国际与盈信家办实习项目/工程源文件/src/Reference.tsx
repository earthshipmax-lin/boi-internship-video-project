import React from 'react';
import {useCurrentFrame} from 'remotion';
import reference from './assets/prototype-reference.json';
export const PrototypeReference:React.FC=()=> <div dangerouslySetInnerHTML={{__html:reference[String(useCurrentFrame()) as keyof typeof reference]??''}}/>;
