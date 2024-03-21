import { React, type AllWidgetProps } from "jimu-core";
import { type IMConfig } from "../config";
import { Providers } from "@withleaf/leaf-link-react";
import { Title } from "../styles/style";
import { getAppStore } from "jimu-core";
import { useEffect, useState } from "react";
import * as geoprocessor from "@arcgis/core/rest/geoprocessor.js";

const getLeafData = async () => {
  const { fullName, id, email } = getAppStore().getState().user;
  const gpUrl = "GP URL";
  const inputParameters = {
    name: fullName,
    email,
    external_id: id,
    expires_in: 90000,
  };

  try {
    const gp = await geoprocessor.execute(gpUrl, inputParameters);

    if (gp.results && gp.results.length > 0 && gp.results[0].value) {
      return JSON.stringify(gp.results[0].value[0]);
    } else {
      console.error("No results found");
      return null;
    }
  } catch (error) {
    console.error("Error executing geoprocessor:", error);
    return null;
  }
};

const Widget = (props: AllWidgetProps<IMConfig>) => {
  const [leafUser, setLeafUser] = useState<string>("");
  const [apiKey, setApiKey] = useState<string>("");

  useEffect(() => {
    const response = getLeafData();
    if (response) {
      setLeafUser(response.value.apiKey);
      setApiKey(response.value.leafUserId);
    }
  }, [leafUser, apiKey]);
  
  return (
    <>
      <Title data-testid="widget-title">{props.config.title}</Title>
      <Providers
        apiKey={apiKey}
        leafUser={leafUser}
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
  );
};

export default Widget;
