import JsSIP from 'jssip'

class SIPService {
  constructor() {
    this.ua = null
    this.session = null
    this.isRegistered = false
    this.localStream = null
    this.remoteStream = null
  }

  configure(config) {
    const socket = new JsSIP.WebSocketInterface(config.wsUrl)

    const configuration = {
      sockets: [socket],
      uri: config.uri,
      password: config.password,
      display_name: config.displayName,
      session_timers: false,
      register: true,
    }

    this.ua = new JsSIP.UA(configuration)

    // Set up event handlers
    this.ua.on('connected', () => {
      console.log('SIP Connected')
    })

    this.ua.on('disconnected', () => {
      console.log('SIP Disconnected')
    })

    this.ua.on('registered', () => {
      console.log('SIP Registered')
      this.isRegistered = true
    })

    this.ua.on('unregistered', () => {
      console.log('SIP Unregistered')
      this.isRegistered = false
    })

    this.ua.on('registrationFailed', (e) => {
      console.error('SIP Registration Failed:', e)
    })

    this.ua.on('newRTCSession', (e) => {
      console.log('New RTC Session')
      this.session = e.session

      // Incoming call
      if (e.originator === 'remote') {
        this.handleIncomingCall(e.session)
      }

      // Session events
      this.session.on('confirmed', () => {
        console.log('Call confirmed')
      })

      this.session.on('ended', () => {
        console.log('Call ended')
        this.cleanupSession()
      })

      this.session.on('failed', () => {
        console.log('Call failed')
        this.cleanupSession()
      })

      this.session.on('peerconnection', (e) => {
        const peerconnection = e.peerconnection

        peerconnection.onaddstream = (event) => {
          this.remoteStream = event.stream
          // Attach to audio element
          const remoteAudio = document.getElementById('remoteAudio')
          if (remoteAudio) {
            remoteAudio.srcObject = this.remoteStream
            remoteAudio.play()
          }
        }
      })
    })
  }

  start() {
    if (this.ua) {
      this.ua.start()
    }
  }

  stop() {
    if (this.ua) {
      this.ua.stop()
    }
  }

  async makeCall(number) {
    if (!this.ua || !this.isRegistered) {
      console.error('SIP UA not registered')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false,
      })

      this.localStream = stream

      const options = {
        mediaConstraints: {
          audio: true,
          video: false,
        },
        mediaStream: stream,
      }

      this.session = this.ua.call(number, options)
    } catch (error) {
      console.error('Error making call:', error)
    }
  }

  answerCall() {
    if (this.session) {
      navigator.mediaDevices
        .getUserMedia({ audio: true, video: false })
        .then((stream) => {
          this.localStream = stream
          const options = {
            mediaConstraints: {
              audio: true,
              video: false,
            },
            mediaStream: stream,
          }
          this.session.answer(options)
        })
        .catch((error) => {
          console.error('Error answering call:', error)
        })
    }
  }

  hangupCall() {
    if (this.session) {
      this.session.terminate()
    }
  }

  holdCall() {
    if (this.session) {
      this.session.hold()
    }
  }

  unholdCall() {
    if (this.session) {
      this.session.unhold()
    }
  }

  muteAudio() {
    if (this.session) {
      this.session.mute({ audio: true })
    }
  }

  unmuteAudio() {
    if (this.session) {
      this.session.unmute({ audio: true })
    }
  }

  handleIncomingCall(session) {
    // Trigger incoming call event
    console.log('Incoming call from:', session.remote_identity.uri.user)
    // You can dispatch an event here to show incoming call UI
  }

  cleanupSession() {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop())
      this.localStream = null
    }
    this.remoteStream = null
    this.session = null
  }
}

export default new SIPService()
