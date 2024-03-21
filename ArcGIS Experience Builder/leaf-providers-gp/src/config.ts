import { type ImmutableObject } from 'seamless-immutable'

export interface Config {
  title: string
  arcGisUserId: string
  isDarkMode: boolean
  companyName: string
  companyLogo: string
  allowedProviders: string[]
  providerWidgetTitle: string
  showSearchbar: boolean
  applications: string[]
  locale: string
}

export type IMConfig = ImmutableObject<Config>
