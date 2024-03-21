import { type ImmutableObject } from 'seamless-immutable'

export interface Config {
  title: string
  arcGisUserId: string
  apiKey: string
  leafUser: string
  isDarkMode: boolean
  companyName: string
  companyLogo: string
  providerName: string
  providerLogo: string
  locale: string
}

export type IMConfig = ImmutableObject<Config>
