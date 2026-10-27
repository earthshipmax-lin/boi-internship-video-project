import {peopleLeadsV13 as originalLeads,peoplePartnersV13,type PeopleContentV13} from './people-content-v13';
export type {PeopleContentV13} from './people-content-v13';
const edits:Record<string,{role?:string;merits?:string[]}>={
 'david-lau':{merits:['30 years in global business leadership','Experience at Marsh, JLT and Willis','CEng · MHKSI · MCSI']},
 'patrick-li':{role:'Senior Advisor to the Group',merits:['Former chief actuary at Prudential HK and AXA','Experience as an appointed actuary','Product strategy and actuarial advice since 2016']},
 'pamela-cheng':{merits:['30 years in insurance operations','Products, marketing and underwriting','Claims and client service']},
 'manli-chan':{merits:['30 years in senior management','Compliance experience at Changjiang Securities and Bank of China','Degrees in social sciences, financial services and law']},
 'ken-yeung':{role:'Marketing & Hong Kong Pension Plans Lead',merits:['20 years in insurance','Experience at AIA, AXA Wealth Management and Convoy','BSc, The Chinese University of Hong Kong']},
 'david-wang':{role:'General Manager, United States',merits:['20 years in finance and insurance','Experience at World Financial Group','Leadership in marketing']},
};
export const peopleLeadsV13:readonly PeopleContentV13[]=originalLeads.map(p=>({...p,role:{...p.role,en:edits[p.id]?.role??p.role.en},merits:{...p.merits,en:edits[p.id]?.merits??p.merits.en}}));
export {peoplePartnersV13};
