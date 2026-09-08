# Candidate Interview Feature Manifest (`src/features/candidate-interview`)

## Purpose
Manages candidate pre-interview lobby preparation, audio hardware testing, LiveKit room connection, and post-interview confirmation UI.

## Component & Hook Mapping

| File Name | Purpose | Key Exports / Dependencies |
| :--- | :--- | :--- |
| `hooks/useMicrophoneTest.ts` | Manages audio stream lifecycle, Web Audio API frequency analysis, device enumeration, and mute toggles. | `useMicrophoneTest`, `UseMicrophoneTestReturn` |
| `components/InterviewerOrb.tsx` | Renders the animated AI Interviewer Orb with speaking, thinking (wavy SVG rings), and listening visual states. | `InterviewerOrb` |
| `components/StageVisualizer.tsx` | Audio spectrum frequency bar visualizer & thinking spinner indicator. | `StageVisualizer` |
| `components/PreInterviewLobby.tsx` | Phase 1 pre-room lobby view (mic test widget, device selector, guidelines, enter room button). | `PreInterviewLobby` |
| `components/PostInterviewCompleted.tsx` | Phase 3 post-interview confirmation view. | `PostInterviewCompleted` |
| `components/MockVoiceStage.tsx` | Phase 2 room stage fallback for offline testing with mock tokens. | `MockVoiceStage` |
| `components/LiveKitVoiceStage.tsx` | Phase 2 live interview stage connecting to LiveKit room audio & voice assistant hook. | `LiveKitVoiceStage` |
