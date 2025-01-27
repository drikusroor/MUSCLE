import React, { useState } from "react";
import {
    Route,
    Redirect,
    RouteComponentProps,
    Switch
} from "react-router-dom";

import Consent from "../Consent/Consent";
import DefaultPage from "../Page/DefaultPage";
import { useExperimentCollection } from "@/API.js";
import Loading from "../Loading/Loading";
import ExperimentCollectionAbout from "./ExperimentCollectionAbout/ExperimentCollectionAbout";
import ExperimentCollectionDashboard from "./ExperimentCollectionDashboard/ExperimentCollectionDashboard";
import { URLS } from "@/config";
import IExperimentCollection from "@/types/ExperimentCollection";
import { useBoundStore } from "@/util/stores";
import { Participant } from "@/types/Participant";

interface RouteParams {
    slug: string
}

interface ExperimentCollectionProps extends RouteComponentProps<RouteParams> {
    participant: Participant
}

const ExperimentCollection = ({ match }: ExperimentCollectionProps) => {
    const [experimentCollection, loadingExperimentCollection] = useExperimentCollection(match.params.slug) as [IExperimentCollection, boolean];
    const [hasShownConsent, setHasShownConsent] = useState(false);
    const participant = useBoundStore((state) => state.participant);
    const participantIdUrl = participant?.participant_id_url;
    const nextExperiment = experimentCollection?.next_experiment;
    const displayDashboard = experimentCollection?.dashboard.length;
    const showConsent = experimentCollection?.consent;

    const onNext = () => {
        setHasShownConsent(true);
    }

    const getExperimentHref = (slug: string) => `/${slug}${participantIdUrl ? `?participant_id=${participantIdUrl}` : ""}`;

    if (loadingExperimentCollection) {
        return (
            <div className="loader-container">
                <Loading />
            </div>
        );
    }

    if (!hasShownConsent && showConsent) {
        const attrs = {
            participant,
            onNext,
            experiment: experimentCollection,
            ...experimentCollection.consent,
        }
        return (
            <DefaultPage className='aha__consent-wrapper' title={experimentCollection.name}>
                <Consent {...attrs}/>
            </DefaultPage>
        )
       
    }

    if (!displayDashboard && nextExperiment) {
        return <Redirect to={getExperimentHref(nextExperiment.slug)} />
    }

    return (
        <div className="aha__collection">
            <Switch>
                <Route path={URLS.experimentCollectionAbout} component={() => <ExperimentCollectionAbout content={experimentCollection?.about_content} slug={experimentCollection.slug} />} />
                <Route path={URLS.experimentCollection} exact component={() => <ExperimentCollectionDashboard experimentCollection={experimentCollection} participantIdUrl={participantIdUrl} />} />
            </Switch>
        </div>
    )
}

export default ExperimentCollection;