import type {Locale} from './locale-v12';

/** Source-checked professional profile copy for the HK Prompt14 people scene.
 * Portrait pixels are copied unchanged; scale limits include the1.04 motion.
 * Source matching is not independent company/person publication approval. */
export type PeopleLocalizedV13=Readonly<Record<Locale,string>>;
export type PeopleMeritsV13=Readonly<Record<Locale,readonly string[]>>;
export type PeopleContentV13=Readonly<{
 id:string;
 file:string;
 nativeWidth:number;
 nativeHeight:number;
 name:PeopleLocalizedV13;
 role:PeopleLocalizedV13;
 merits:PeopleMeritsV13;
 fit:'contain'|'cover';
 maxScale:1.6;
 source:Readonly<{page:number;xref:number;sha256:string}>;
}>;

export const peopleLeadsV13:readonly PeopleContentV13[]=[
 {
  id:'david-lau',file:'stills/hk-v13-people/david-lau.png',nativeWidth:2015,nativeHeight:1657,
  name:{yue:'劉天生 David Lau',en:'David Lau','zh-CN':'刘天生 David Lau'},
  role:{yue:'集團首席執行官',en:'Group Chief Executive Officer','zh-CN':'集团首席执行官'},
  merits:{
   yue:['30年跨國企業高管經驗','曾任職達信、怡和、韋萊等國際企業','CEng · MHKSI · MCSI'],
   en:['30 years in multinational leadership','Experience at Marsh, JLT and Willis','CEng · MHKSI · MCSI'],
   'zh-CN':['30年跨国企业高管经验','曾任职达信、怡和、韦莱等国际企业','CEng · MHKSI · MCSI'],
  },
  fit:'cover',maxScale:1.6,
  source:{page:17,xref:3721,sha256:'3a14150c12c7c9d695d5e05581360376995bdd1c551eced454b9048960236f58'},
 },
 {
  id:'patrick-li',file:'stills/hk-v13-people/patrick-li.png',nativeWidth:787,nativeHeight:443,
  name:{yue:'李冠成 Patrick Li',en:'Patrick Li','zh-CN':'李冠成 Patrick Li'},
  role:{yue:'集團高級顧問',en:'Group Senior Adviser','zh-CN':'集团高级顾问'},
  merits:{
   yue:['曾任香港保誠、安盛總精算師','委任精算師經歷','2016年起提供產品策略與精算意見'],
   en:['Former chief actuary at Prudential HK and AXA','Appointed actuary experience','Product strategy and actuarial advice since 2016'],
   'zh-CN':['曾任香港保诚、安盛总精算师','委任精算师经历','2016年起提供产品策略与精算意见'],
  },
  fit:'cover',maxScale:1.6,
  source:{page:18,xref:521,sha256:'a9da8873df036864c993d97e52e7f58a8fe7c88593d0d6167497e1b0b5c60b5f'},
 },
 {
  id:'pamela-cheng',file:'stills/hk-v13-people/pamela-cheng.png',nativeWidth:386,nativeHeight:371,
  name:{yue:'鄭健麗 Pamela Cheng',en:'Pamela Cheng','zh-CN':'郑健丽 Pamela Cheng'},
  role:{yue:'首席營運官',en:'Chief Operating Officer','zh-CN':'首席营运官'},
  merits:{
   yue:['30年保險業實操經驗','貫通產品、營銷、核保','涵蓋理賠、客戶服務'],
   en:['30 years of insurance operations','Product, marketing and underwriting','Claims and customer service'],
   'zh-CN':['30年保险业实操经验','贯通产品、营销、核保','涵盖理赔、客户服务'],
  },
  fit:'contain',maxScale:1.6,
  source:{page:18,xref:527,sha256:'7b717261f1b415a1dec1f20cb404027580e302da41a82d2609742e2beca098aa'},
 },
 {
  id:'manli-chan',file:'stills/hk-v13-people/manli-chan.png',nativeWidth:748,nativeHeight:535,
  name:{yue:'陳萬里 Manli Chan',en:'Manli Chan','zh-CN':'陈万里 Manli Chan'},
  role:{yue:'公司負責人 RO',en:'Responsible Officer (RO)','zh-CN':'公司负责人 RO'},
  merits:{
   yue:['30年高管經驗','長江證券、中國銀行合規經歷','社會科學、金融服務、法律三學位'],
   en:['30 years in senior management','Compliance at Changjiang Securities and Bank of China','Degrees in social sciences, financial services and law'],
   'zh-CN':['30年高管经验','长江证券、中国银行合规经历','社会科学、金融服务、法律三学位'],
  },
  fit:'cover',maxScale:1.6,
  source:{page:18,xref:524,sha256:'8b8e27ed3b6c764a495f4091a1b824332e223f93c7663e9c8b852a1ca3df2bcf'},
 },
 {
  id:'ken-yeung',file:'stills/hk-v13-people/ken-yeung.png',nativeWidth:705,nativeHeight:556,
  name:{yue:'楊金印 Ken Yeung',en:'Ken Yeung','zh-CN':'杨金印 Ken Yeung'},
  role:{yue:'市場營運 · 強積金負責人',en:'Marketing Operations & MPF Lead','zh-CN':'市场营运 · 强积金负责人'},
  merits:{
   yue:['20年保險經驗','友邦、安盛財富管理、康宏任職經歷','香港中文大學理學士'],
   en:['20 years in insurance','AIA, AXA Wealth Management and Convoy experience','BSc, The Chinese University of Hong Kong'],
   'zh-CN':['20年保险经验','友邦、安盛财富管理、康宏任职经历','香港中文大学理学士'],
  },
  fit:'cover',maxScale:1.6,
  source:{page:18,xref:518,sha256:'4f1c268a17ed9185087b28185c0b9f9d4874cd3e803de6538a64c26f4deb4bc0'},
 },
 {
  id:'david-wang',file:'stills/hk-v13-people/david-wang.png',nativeWidth:335,nativeHeight:382,
  name:{yue:'王浩 David Wang',en:'David Wang','zh-CN':'王浩 David Wang'},
  role:{yue:'美國總經理',en:'US General Manager','zh-CN':'美国总经理'},
  merits:{
   yue:['20年金融保險經驗','世界金融集團','執行營銷總監經歷'],
   en:['20 years in finance and insurance','World Financial Group','Executive marketing director experience'],
   'zh-CN':['20年金融保险经验','世界金融集团','执行营销总监经历'],
  },
  fit:'contain',maxScale:1.6,
  source:{page:19,xref:538,sha256:'3a45419fea3a89bf7a4ba2b4fdfa1833245054f4bc9b4c5b375e2abc6e76a03b'},
 },
];

const noMerits:PeopleMeritsV13={yue:[],en:[],'zh-CN':[]};
const partnerRole:PeopleLocalizedV13={yue:'美國高級合夥人',en:'US Senior Partner','zh-CN':'美国高级合伙人'};
export const peoplePartnersV13:readonly PeopleContentV13[]=[
 {id:'lily-ku',file:'stills/hk-v13-people/lily-ku.png',nativeWidth:430,nativeHeight:425,
  name:{yue:'谷林麗 Lily Ku',en:'Lily Ku','zh-CN':'谷林丽 Lily Ku'},role:partnerRole,merits:noMerits,fit:'cover',maxScale:1.6,
  source:{page:19,xref:3928,sha256:'f5f08fb41f1953d0d054882146e8651027ffd175a1e1be95340544250388dbf6'}},
 {id:'noah-cheung',file:'stills/hk-v13-people/noah-cheung.png',nativeWidth:297,nativeHeight:364,
  name:{yue:'張志凌 Noah Cheung',en:'Noah Cheung','zh-CN':'张志凌 Noah Cheung'},role:partnerRole,merits:noMerits,fit:'cover',maxScale:1.6,
  source:{page:19,xref:544,sha256:'a3981f5b97805a2a67498960791581715ab57d309233bc76c9fe8efc1cd6aaa8'}},
 {id:'catherine-luo',file:'stills/hk-v13-people/catherine-luo.png',nativeWidth:320,nativeHeight:398,
  name:{yue:'羅英姿 Catherine Luo',en:'Catherine Luo','zh-CN':'罗英姿 Catherine Luo'},role:partnerRole,merits:noMerits,fit:'cover',maxScale:1.6,
  source:{page:19,xref:541,sha256:'ebda4a375f85630c2630d098d08d579556d24cf933b8ab493ef617a328a0bcd7'}},
 {id:'vivian-mau',file:'stills/hk-v13-people/vivian-mau.png',nativeWidth:282,nativeHeight:282,
  name:{yue:'胡忠瑤 Vivian Mau',en:'Vivian Mau','zh-CN':'胡忠瑶 Vivian Mau'},role:partnerRole,merits:noMerits,fit:'cover',maxScale:1.6,
  source:{page:19,xref:549,sha256:'e48bf69ce9689811ce57d37b1617c5c065c5941e2eeaa9cc6ce9e79585af52d9'}},
 {id:'crystal-wang',file:'stills/hk-v13-people/crystal-wang.png',nativeWidth:474,nativeHeight:571,
  name:{yue:'王娟 Crystal Wang',en:'Crystal Wang','zh-CN':'王娟 Crystal Wang'},role:partnerRole,merits:noMerits,fit:'cover',maxScale:1.6,
  source:{page:19,xref:547,sha256:'45de0861575a2db126123ae91f8356b76a3176e68038a294f8b1c07c6eeae66e'}},
];

export const peopleCopyNotesV13={
 source:'qa/v13/people/content-check.md',
 rawAssets:'qa/v13/people/people-source.json',
 publicAssetAudit:'qa/v13/people/people-public-assets.json',
 davidLau:'Use source-supported company experience summary; do not repeat Prompt14 mismatched company/job titles.',
 davidWang:'Source gives two achievements. The three display fragments split the company and executive role, without inventing a third achievement or a departure date.',
 crystalWang:'Wang follows page16 organization chart; page19 Wan remains documented in content-check.',
 lowResolutionLayout:'User approved original-aspect warm-gray padding, with total native scale including animation<=1.6.',
} as const;
