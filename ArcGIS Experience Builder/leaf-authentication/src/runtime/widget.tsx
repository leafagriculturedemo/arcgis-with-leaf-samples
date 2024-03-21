import { React, type AllWidgetProps } from 'jimu-core'
import { type IMConfig } from '../config'
import { Authentication } from '@withleaf/leaf-link-react'
import { Title } from '../styles/style'

const Widget = (props: AllWidgetProps<IMConfig>) => {
  return (
    <>
      <Title data-testid="widget-title">{props.config.title}</Title>
      <Authentication
        apiKey={props.config.apiKey}
        leafUser={props.config.leafUser}
        isDarkMode={props.config.isDarkMode}
        companyName={props.config.companyName}
        companyLogo={props.config.companyLogo}
        providerName={props.config.providerName}
        providerLogo={props.config.providerLogo}
        locale={props.config.locale}
      />
    </>
  )
}

export default Widget
