/**
 * Browser Web Speech API wrapper for STT + TTS
 * Uses MediaRecorder + Backend API for transcription (Groq Whisper)
 * Uses window.speechSynthesis for audio playback
 */

export class SpeechRecognizer {
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: BlobPart[] = []
  private isRecording = false

  async start(onResult: (transcript: string, isFinal: boolean) => void, onError?: (error: string) => void) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      onError?.('Microphone access not supported by browser')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      this.mediaRecorder = new MediaRecorder(stream)
      this.audioChunks = []
      this.isRecording = true

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.onstop = async () => {
        this.isRecording = false
        // Stop all tracks to release mic
        stream.getTracks().forEach(track => track.stop())
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
        this.audioChunks = []
        
        // Send to backend
        try {
          const formData = new FormData()
          formData.append('audio', audioBlob, 'recording.webm')
          
          const token = localStorage.getItem('refund_agent_token')
          const headers: HeadersInit = {}
          if (token) headers['Authorization'] = `Bearer ${token}`

          const response = await fetch('/api/voice/transcribe', {
            method: 'POST',
            headers,
            body: formData
          })
          
          if (!response.ok) {
            throw new Error(`Failed to transcribe: ${response.statusText}`)
          }
          
          const data = await response.json()
          if (data.text) {
            onResult(data.text, true)
          }
        } catch (e: any) {
          console.error('[Speech] Transcription error:', e)
          onError?.(e.message || 'Failed to transcribe audio')
        }
      }

      this.mediaRecorder.start()
      console.log('[Speech] Recording started')
    } catch (e: any) {
      console.error('[Speech] Failed to start microphone:', e)
      onError?.('Could not access microphone. Please check permissions.')
    }
  }

  stop() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop()
      console.log('[Speech] Recording stopped, processing...')
    }
  }

  abort() {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop()
    }
  }

  isActive(): boolean {
    return this.isRecording
  }

  isSupported(): boolean {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  }
}

export class SpeechSynthesizer {
  private voices: SpeechSynthesisVoice[] = []

  constructor() {
    // Load voices ASAP to ensure they are available when speak() is called
    if (window.speechSynthesis) {
      this.voices = window.speechSynthesis.getVoices()
      window.speechSynthesis.onvoiceschanged = () => {
        this.voices = window.speechSynthesis.getVoices()
      }
    }
  }

  speak(text: string, onEnd?: () => void) {
    if (!window.speechSynthesis) {
      console.warn('[TTS] Speech Synthesis not supported')
      return
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.0
    utterance.pitch = 1.2 // Higher pitch for female voice
    utterance.volume = 1.0

    const voices = this.voices.length > 0 ? this.voices : window.speechSynthesis.getVoices()
    
    if (voices.length > 0) {
      // Find female voice
      const femaleVoice = voices.find(v => 
        v.name.toLowerCase().includes('female') || 
        v.name.toLowerCase().includes('zira') || 
        v.name.toLowerCase().includes('samantha') || 
        v.name.toLowerCase().includes('victoria') ||
        v.name.toLowerCase().includes('karen') ||
        v.name.toLowerCase().includes('moira') ||
        v.name.toLowerCase().includes('tessa') ||
        v.name.toLowerCase().includes('google uk english female')
      )
      
      if (femaleVoice) {
        utterance.voice = femaleVoice
      } else {
        // Fallback
        const engVoice = voices.find(v => v.lang.startsWith('en'))
        if (engVoice) utterance.voice = engVoice
      }
    }

    utterance.onend = () => {
      console.log('[TTS] Speaking ended')
      onEnd?.()
    }

    utterance.onerror = (event) => {
      console.error('[TTS] Error:', event.error)
    }

    window.speechSynthesis.speak(utterance)
  }

  stop() {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
  }

  isSpeaking(): boolean {
    return window.speechSynthesis?.speaking ?? false
  }

  isSupported(): boolean {
    return !!window.speechSynthesis
  }
}

export class VoiceController {
  private recognizer: SpeechRecognizer
  private synthesizer: SpeechSynthesizer
  constructor() {
    this.recognizer = new SpeechRecognizer()
    this.synthesizer = new SpeechSynthesizer()
  }

  isSupported(): boolean {
    return this.synthesizer.isSupported() || this.recognizer.isSupported()
  }

  startListening(
    onTranscript: (text: string, isFinal: boolean) => void,
    onError?: (error: string) => void
  ) {
    if (!this.recognizer.isSupported()) {
      onError?.('Voice recognition not supported')
      return
    }
    this.recognizer.start(onTranscript, onError)
  }

  stopListening() {
    this.recognizer.stop()
  }

  speak(text: string, onEnd?: () => void) {
    if (!this.synthesizer.isSupported()) return
    this.synthesizer.speak(text, onEnd)
  }

  stopSpeaking() {
    this.synthesizer.stop()
  }

  isListening(): boolean {
    return this.recognizer.isActive()
  }

  isSpeaking(): boolean {
    return this.synthesizer.isSpeaking()
  }
}
