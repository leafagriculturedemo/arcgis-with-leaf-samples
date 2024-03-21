import { React, type AllWidgetProps } from 'jimu-core'
import { type IMConfig } from '../config'
import { FileUpload } from '@withleaf/leaf-link-react'
import { Title } from '../styles/style'

const Widget = (props: AllWidgetProps<IMConfig>) => {
  return (
    <>
      <Title data-testid="file-upload-title">{props.config.title}</Title>
      <FileUpload
        apiKey={props.config.apiKey}
        leafUser={props.config.leafUser}
        isDarkMode={props.config.isDarkMode}
        companyName={props.config.companyName}
        companyLogo={props.config.companyLogo}
        filesTimeRange={props.config.filesTimeRange}
        title={props.config.uploadWidgetTitle}
        locale={props.config.locale}
      />
    </>
  )
}

export default Widget
