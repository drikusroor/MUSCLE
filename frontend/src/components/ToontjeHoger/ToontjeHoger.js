import React, { useEffect, useState, useRef } from "react";
import { LOGO_TITLE } from "../../config";
import { Switch, Route, Link } from "react-router-dom";
import Rank from "../Rank/Rank";

const LOGO_URL = "/images/experiments/toontjehoger/logo.svg";

const Logo = ({ homeUrl }) => (
    <Link
        to={homeUrl}
        className="logo"
        style={{ backgroundImage: `url(${LOGO_URL}` }}
    >
        {LOGO_TITLE}
    </Link>
);

const Supporters = ({ intro }) => (
    <div className="supporters">
        <p>{intro}</p>
        <div className="organizations">
            <a
                href="https://www.knaw.nl"
                target="_blank"
                rel="noopener noreferrer"
                className="knaw"
            >
                <img
                    src="/images/experiments/toontjehoger/logo-knaw-white.svg"
                    alt="KNAW"
                />
            </a>
            <a
                href="https://www.amsterdammusiclab.nl"
                target="_blank"
                rel="noopener noreferrer"
                className="aml"
            >
                <img
                    src="/images/logo-full-white.svg"
                    alt="Amsterdam Music Lab"
                />
            </a>
        </div>
    </div>
);

const useAnimatedScore = (targetScore) => {
    const [score, setScore] = useState(0);

    const scoreValue = useRef(0);

    useEffect(() => {
        if (targetScore === 0) {
            return;
        }

        let id = -1;

        const nextStep = () => {
            // Score step
            const scoreStep = Math.max(
                1,
                Math.min(
                    10,
                    Math.ceil(Math.abs(scoreValue.current - targetScore) / 10)
                )
            );

            // Scores are equal, stop
            if (targetScore === scoreValue.current) {
                return;
            }

            // Add / subtract score
            scoreValue.current +=
                Math.sign(targetScore - scoreValue.current) * scoreStep;
            setScore(scoreValue.current);

            id = setTimeout(nextStep, 50);
        };
        id = setTimeout(nextStep, 50);

        return () => {
            window.clearTimeout(id);
        };
    }, [targetScore]);

    return score;
};

const Score = ({ score, label, scoreClass }) => {
    const currentScore = useAnimatedScore(score);

    return (
        <div className="score">
            <Rank rank={{ class: scoreClass }} />
            <h3>
                {currentScore ? currentScore + " " : ""}
                {label}
            </h3>
        </div>
    );
};

// ToontjeHoger is an experiment view that shows the ToontjeHoger home
const ToontjeHogerHome = ({ experiment, config, experiments }) => {
    return (
        <div className="aha__toontjehoger">
            <Logo homeUrl={`/${experiment.slug}`} />

            {/* Hero */}
            <div className="hero">
                <div className="intro">
                    <h1>{config.payoff}</h1>
                    <p>{config.intro}</p>
                    <div className="actions">
                        {config.main_button_label && (
                            <Link
                                className="btn btn-lg btn-primary"
                                to={config.main_button_url}
                            >
                                {config.main_button_label}
                            </Link>
                        )}
                        {config.intro_read_more && (
                            <Link
                                className="btn btn-lg btn-outline-primary"
                                to={`/${experiment.slug}/about`}
                            >
                                {config.intro_read_more}
                            </Link>
                        )}
                    </div>
                </div>

                <div className="results">
                    <Score
                        score={config.score}
                        scoreClass={config.score_class}
                        label={config.score_label}
                    />
                </div>
            </div>

            {/* Experiments */}
            <div className="experiments">
                <ul>
                    {experiments.map((experiment) => (
                        <li
                            key={experiment.slug}
                            style={{
                                borderBottom: `5px solid ${experiment.color}`,
                            }}
                        >
                            <Link to={"/" + experiment.slug}>
                                <div
                                    className="image"
                                    style={{
                                        backgroundImage: `url(${experiment.image})`,
                                        backgroundColor: experiment.color,
                                    }}
                                ></div>
                                <h3>{experiment.title}</h3>
                                <p>{experiment.description}</p>
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Supporters */}
            <Supporters intro={config.supporters_intro} />
        </div>
    );
};

// ToontjeHoger is an experiment view that shows the ToontjeHoger home
const ToontjeHogerAbout = ({ experiment, config, experiments }) => {
    return (
        <div className="aha__toontjehoger">
            <Logo homeUrl={`/${experiment.slug}`} />

            <h1 style={{ textAlign: "center" }}>TODO!</h1>

            {/* Supporters */}
            <Supporters intro={config.supporters_intro} />
        </div>
    );
};

const ToontjeHoger = (props) => {
    return props.experiment ? (
        <>
            <Switch>
                <Route path={`/${props.experiment.slug}/about`} exact>
                    <ToontjeHogerAbout {...props} />
                </Route>
                <Route path="*">
                    <ToontjeHogerHome {...props} />
                </Route>
            </Switch>
        </>
    ) : null;
};

export default ToontjeHoger;
