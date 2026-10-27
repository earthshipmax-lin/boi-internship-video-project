import type {Locale} from './locale-v12';
/** The old38-item inventory omitted the separate bank-row label. Keep that
 * sole additional UI phrase in a strict locale table, never inside a Scene. */
export const screenCopyExtrasV13={banks:{yue:'銀行',en:'Banks','zh-CN':'银行'}} as const satisfies Record<string,Record<Locale,string>>;
export const getScreenCopyExtraV13=(locale:Locale,key:keyof typeof screenCopyExtrasV13)=>screenCopyExtrasV13[key][locale];
