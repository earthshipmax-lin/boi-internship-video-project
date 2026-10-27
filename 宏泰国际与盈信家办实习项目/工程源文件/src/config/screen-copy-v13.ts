import {captionCuesV12,untranslatedInventoryV12,type Locale} from './locale-v12';
import {peopleLeadsV13,peoplePartnersV13} from './people-content-v13';

/** Complete UI-copy coverage for the38 previously inventoried screen items.
 * This module does not edit approved captions, timing, components or artwork. */
export type ScreenInventoryIdV13=typeof untranslatedInventoryV12[number]['id'];
export type ScreenLocaleTextV13=Readonly<Record<Locale,string>>;
type TextEntryV13=Readonly<{
 kind:'text';sourceWording:string;basis:'translation-derived';text:ScreenLocaleTextV13;
 notes:string;existingTableEnglishReference?:string;
}>;
type PeopleEntryV13=Readonly<{
 kind:'people-content-reference';sourceWording:string;basis:'source-checked-existing-people-config';
 module:'src/config/people-content-v13.ts';leads:typeof peopleLeadsV13;partners:typeof peoplePartnersV13;
 notes:string;
}>;
type EntryV13=TextEntryV13|PeopleEntryV13;
const text=(sourceWording:string,en:string,cn:string,notes='',yue=sourceWording):TextEntryV13=>({
 kind:'text',sourceWording,basis:'translation-derived',text:{yue,en,'zh-CN':cn},notes,
});
const tableEnglish=(id:string):string=>{
 const cue=captionCuesV12.find(x=>x.id===id);
 if(!cue)throw new Error(`Missing approved caption reference ${id}`);
 return cue.text.en;
};
const tablePhrase=(sourceWording:string,cn:string,id:string,notes=''):TextEntryV13=>({
 ...text(sourceWording,tableEnglish(id),cn,notes),existingTableEnglishReference:id,
});

export const screenCopyV13={
 'meta.vision':text('每一個家族的未來','The future of every family','每一个家族的未来'),
 'meta.origin':text('時間 · 專業 · 信任','Time · Expertise · Trust','时间 · 专业 · 信任'),
 'meta.premium':text('01 / 集團實力','01 / Group strength','01 / 集团实力'),
 'meta.commission':text('02 / 集團實力','02 / Group strength','02 / 集团实力'),
 'meta.clients':text('03 / 集團實力','03 / Group strength','03 / 集团实力'),
 'meta.awards':text('專業的積累','Expertise built over time','专业的积累'),
 'meta.map':text('全球視野 · 一路向前','Global vision · Moving forward','全球视野 · 一路向前'),
 'meta.platform':text('家族辦公室平台','Family office platform','家族办公室平台'),
 'meta.offices':text('三城辦公室 · 公司實景','Offices in three cities · Company premises','三城办公室 · 公司实景'),
 'meta.roots':text('根深 · 步穩 · 向前','Deep roots · Steady steps · Forward','根深 · 步稳 · 向前'),
 'origin.label':text('集團源自','Group origins','集团源自','Origins wording is retained; this is not a new claim that the present legal entity was incorporated in1997.'),
 'origin.year':text('1997年','1997','1997年','Only the language-specific year unit is removed in English.'),
 'origin.support':text('一路走來，承接每一份信任。','Carrying trust forward, every step of the way.','一路走来，承接每一份信任。'),
 'premium.label':text('集團總保費','Group total premiums','集团总保费'),
 'commission.label':text('集團總佣金','Group total commission','集团总佣金'),
 'data.values':text('100億+ / 15億+ / 2萬+','HK$10B+ / HK$1.5B+ / 20,000+','100亿+ / 15亿+ / 2万+',
  '1亿=100 million.100亿=10 billion;15亿=1.5 billion. Financial facts are inherited from source, not independently reverified here.'),
 'data.currency':text('港元','Hong Kong dollars','港元'),
 'clients.label':text('高淨值客戶','High-net-worth clients','高净值客户'),
 'clients.support':text('數字背後，是信任。','Behind the numbers is trust.','数字背后，是信任。'),
 'map.title':text('讓眼光，跨越地域。','Let vision cross borders.','让眼光，跨越地域。',
  'This imperative UI title is distinct from caption19. Approved caption wording is not replaced.'),
 'map.singapore-status':text('籌備中','In preparation','筹备中','Preparation status is preserved; not an operational-office claim.'),
 'map.regional-title':text('香港 — 深圳 · 12×','Hong Kong — Shenzhen · 48×','香港 — 深圳 · 48×',
  'Source inventory said12×. The implemented geographic magnifier is48× and must be labelled truthfully; no false12× label.',
  '香港 — 深圳 · 48×'),
 'offices.headline':tablePhrase('看得全面。行得長遠。','看得全面。行得长远。','caption-18',
  'English reuses the existing table phrase exactly, without modifying caption18 or its cue.'),
 'offices.vision-title':tablePhrase('眼光，跨越地域。','眼光，跨越地域。','caption-19'),
 'offices.hk-address':text('尖沙咀 · 新港中心','Tsim Sha Tsui · Silvercord','尖沙咀 · 新港中心',
  'Building-level label only. Silvercord also appears in the existing offices-assets-v12 source description; no unit or new address is added.'),
 'offices.sz-address':text('南山 · 康泰創新廣場','Nanshan · Kangtai Innovation Plaza','南山 · 康泰创新广场',
  'Kangtai is a transliteration of康泰; Innovation Plaza translates创新广场. This is not a claim of an independently verified official English building trademark.'),
 'offices.ny-address':text('Flushing · New York','Flushing · New York','法拉盛 · 纽约',
  'English remains the existing source wording; Chinese localizes the same two place names.'),
 'values.title':tablePhrase('信任，扎根時間。','信任，扎根时间。','caption-20'),
 'roots.title':tablePhrase('根扎得深，\n長得更高。','根扎得深，\n长得更高。','caption-21',
  'English phrase is unchanged from the existing table; line breaks remain a future layout choice.'),
 'platform.sectors':text('核心保險業務 / 家族辦公室 / 財富管理','Core insurance / Family office / Wealth management','核心保险业务 / 家族办公室 / 财富管理'),
 'platform.nodes':text('保險 / 信託 / 稅務 / 教育 / 身份','Insurance / Trusts / Tax / Education / Residency','保险 / 信托 / 税务 / 教育 / 身份',
  'Residency follows the existing table phrase Education and residency planning; no immigration outcome is promised.'),
 'platform.insurance-evidence':text('香港 · 澳門 · 美國 / 百慕達 · 新加坡','Hong Kong · Macau · USA / Bermuda · Singapore','香港 · 澳门 · 美国 / 百慕达 · 新加坡'),
 'platform.wealth-evidence':text('信託 · 遺產 / 稅務規劃','Trusts · Estates / Tax planning','信托 · 遗产 / 税务规划'),
 'platform.family-evidence':text('盈信家辦 EVERGREEN','Evergreen Family Office','盈信家办 EVERGREEN',
  'Translated screen label only. Official Evergreen artwork is preserved separately.'),
 'legal.licences':text('保監局持牌 FB1681 · PIBA會員 M0573','IA licence FB1681 · PIBA member M0573','保监局持牌 FB1681 · PIBA会员 M0573',
  'Insurance Authority licence and PIBA membership remain distinct; this is not a fresh verification of current regulatory status.'),
 'legal.compliance':text('全面風險管理 · 合規操作準則 · 客戶隱私保護 · 業務持續運營',
  'Comprehensive risk management · Compliance procedures · Client privacy protection · Business continuity',
  '全面风险管理 · 合规操作准则 · 客户隐私保护 · 业务持续运营'),
 'awards.couplet-labels':text('永明金融 SUN LIFE / 友邦 AIA','Sun Life / AIA','永明金融 SUN LIFE / 友邦 AIA',
  'Exact existing AwardsStage10 donor labels; p5 donor inscriptions support the assignment.'),
 'people.names-roles-merits':{
  kind:'people-content-reference',sourceWording:'六位主角姓名／職銜／功績及五位合夥人姓名／職銜',
  basis:'source-checked-existing-people-config',module:'src/config/people-content-v13.ts',
  leads:peopleLeadsV13,partners:peoplePartnersV13,
  notes:'Direct reference to the existing source-checked arrays; no duplicate people wording is maintained here.',
 },
} as const satisfies Readonly<Record<ScreenInventoryIdV13,EntryV13>>;

export type TextScreenCopyIdV13=Exclude<ScreenInventoryIdV13,'people.names-roles-merits'>;
/** Strict lookup: no Chinese/other-language fallback is supplied. */
export const getScreenCopyV13=(locale:Locale,id:TextScreenCopyIdV13):string=>screenCopyV13[id].text[locale];
const grouped=(locale:Locale,id:TextScreenCopyIdV13)=>getScreenCopyV13(locale,id).split(' / ');
export const getNumericScreenValuesV13=(locale:Locale)=>{
 const [premium,commission,clients]=grouped(locale,'data.values');return {premium,commission,clients};
};
export const getPlatformScreenCopyV13=(locale:Locale)=>({
 sectors:grouped(locale,'platform.sectors'),nodes:grouped(locale,'platform.nodes'),
 insuranceEvidenceLines:grouped(locale,'platform.insurance-evidence'),
 wealthEvidenceLines:grouped(locale,'platform.wealth-evidence'),
 familyEvidence:getScreenCopyV13(locale,'platform.family-evidence'),
});
export const getCoupletScreenLabelsV13=(locale:Locale)=>grouped(locale,'awards.couplet-labels');
export const getPeopleScreenCopyV13=(locale:Locale)=>({
 leads:peopleLeadsV13.map(p=>({id:p.id,name:p.name[locale],role:p.role[locale],merits:p.merits[locale]})),
 partners:peoplePartnersV13.map(p=>({id:p.id,name:p.name[locale],role:p.role[locale],merits:p.merits[locale]})),
});

export const screenAssetLanguageExceptionsV13=[
 {kind:'official_brand_svg',source:'Original supplied Hong Tai/Blue Oak and Evergreen SVG assets',policy:'Preserve original paths, colours and embedded Chinese/English brand lettering. Do not reletter artwork by locale.'},
 {kind:'source_portrait_photo',source:'Original PDF pixels and original soft masks',policy:'Embedded signage, clothing or source background lettering stays original; not a UI translation fallback.'},
 {kind:'source_certificate_and_couplet',source:'Original PDF certificates, awards and complete couplet photographs',policy:'Do not translate, mirror or rewrite lettering inside source images. Translate only separately rendered donor labels.'},
 {kind:'source_office_photo',source:'Original PDF office photographs',policy:'Embedded physical signs stay unchanged; separately rendered city/building labels use locale copy.'},
] as const;

const inventoryIds=untranslatedInventoryV12.map(x=>x.id);
const coverageIds=Object.keys(screenCopyV13) as ScreenInventoryIdV13[];
export const screenTranslationCoverageV13={
 status:'copy_prepared_pending_full_scene_fit',expectedCount:inventoryIds.length,coveredCount:coverageIds.length,
 missingIds:inventoryIds.filter(id=>!coverageIds.includes(id)),extraIds:coverageIds.filter(id=>!inventoryIds.includes(id)),
 sourceInventory:'src/config/locale-v12.ts:untranslatedInventoryV12',
 textEntryCount:37,delegatedPeopleEntryCount:1,englishFontForFutureScene:'Geist',
 fallback:null,rootIntegrated:false,finalRenderValidated:false,
} as const;
