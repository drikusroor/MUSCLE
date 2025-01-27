import Trial from "../components/Trial/Trial";

export default {
    title: "Trial",
    component: Trial,
    parameters: {
        layout: "fullscreen",
    },
};

const getDefaultArgs = (overrides = {}) => ({
    html: {
        body: "<p>This is <u>the</u> <b>HTML</b> <i>body</i></p>",
    },
    config: {
        style: "AUTOPLAY",
        auto_advance: true,
        response_time: 1000,
        continue_label: "Continue",
        show_continue_button: true,
    },
    playback: {
        view: "BUTTON",
        instruction: "This is the instruction",
        preload_message: "This is the preload message",
        play_config: {
            autoplay: true,
            controls: true,
            loop: true,
            muted: true,
            playback_rate: 1,
            preload: "auto",
        },
        sections: [
            {
                start: 0,
                end: 10,
                text: "This is the first section",
            },
            {
                start: 10,
                end: 20,
                text: "This is the second section",
            },
        ],
    },
    feedback_form: {
        form: [
            {
                key: "know_song",
                view: "BUTTON_ARRAY",
                explainer: "",
                question: "1. Do you know this song?",
                result_id: 17242,
                is_skippable: false,
                submits: false,
                style: "boolean",
                choices: {
                    yes: "fa-check",
                    unsure: "fa-question",
                    no: "fa-xmark",
                },
                min_values: 1,
            },
            {
                key: "like_song",
                view: "ICON_RANGE",
                explainer: "",
                question: "2. How much do you like this song?",
                result_id: 17241,
                is_skippable: false,
                submits: false,
                style: "gradient-7",
                choices: {
                    1: "fa-face-grin-hearts",
                    2: "fa-face-grin",
                    3: "fa-face-smile",
                    4: "fa-face-meh",
                    5: "fa-face-frown",
                    6: "fa-face-frown-open",
                    7: "fa-face-angry",
                },
            },
        ],
        submit_label: "Submit",
        skip_label: "Skip",
        is_skippable: true,
        is_profile: true,
    },
    onNext: () => {},
    onResult: () => {},
    ...overrides,
});

export const Default = {
    args: getDefaultArgs(),
    decorators: [
        (Story) => (
            <div
                style={{ width: "100%", height: "100%", backgroundColor: "#fff", padding: "1rem" }}
            >
                <Story />
            </div>
        ),
    ],
};

export const BooleanColorScheme = {
    args: getDefaultArgs({
        config: {
            style: "boolean",
            auto_advance: true,
            response_time: 1000,
            continue_label: "Continue",
            show_continue_button: true,
        },
    }),
    decorators: [
        (Story) => (
            <div
                style={{ width: "100%", height: "100%", backgroundColor: "#fff", padding: "1rem" }}
            >
                <Story />
            </div>
        ),
    ],
};

export const BooleanNegativeFirstColorScheme = {
    args: getDefaultArgs({
        config: {
            style: "boolean-negative-first",
            auto_advance: true,
            response_time: 1000,
            continue_label: "Continue",
            show_continue_button: true,
        },
    }),
    decorators: [
        (Story) => (
            <div
                style={{ width: "100%", height: "100%", backgroundColor: "#fff", padding: "1rem" }}
            >
                <Story />
            </div>
        ),
    ],
};

export const NeutralColorScheme = {
    args: getDefaultArgs({
        config: {
            style: "neutral",
            auto_advance: true,
            response_time: 1000,
            continue_label: "Continue",
            show_continue_button: true,
        },
    }),
    decorators: [
        (Story) => (
            <div
                style={{ width: "100%", height: "100%", backgroundColor: "#fff", padding: "1rem" }}
            >
                <Story />
            </div>
        ),
    ],
};

export const NeutralInvertedColorScheme = {
    args: getDefaultArgs({
        config: {
            style: "neutral-inverted",
            auto_advance: true,
            response_time: 1000,
            continue_label: "Continue",
            show_continue_button: true,
        },
    }),
    decorators: [
        (Story) => (
            <div
                style={{ width: "100%", height: "100%", backgroundColor: "#fff", padding: "1rem" }}
            >
                <Story />
            </div>
        ),
    ],
};
