import { React, type AllWidgetProps } from 'jimu-core'
import { type IMConfig } from '../config'
import { Providers } from '@withleaf/leaf-link-react'
import { Title } from '../styles/style'

const Widget = (props: AllWidgetProps<IMConfig>) => {
  return (
    <>
      <Title data-testid="providers-title">{props.config.title}</Title>
      <Providers
        apiKey={props.config.apiKey}
        leafUser={props.config.leafUser}
        isDarkMode={props.config.isDarkMode}
        companyName={props.config.companyName}
        companyLogo={props.config.companyLogo}
        allowedProviders={props.config.allowedProviders}
        title={props.config.providerWidgetTitle}
        showSearchbar={props.config.showSearchbar}
        applications={props.config.applications}
        locale={props.config.locale}
      />
    </>
  )
}

export default Widget
