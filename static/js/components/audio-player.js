// Audio player component
class AudioPlayer {
    constructor() {
        this.audio = new Audio();
        this.isPlaying = false;
        this.currentTrack = null;
        
        this.init();
    }
    
    init() {
        // Play button handlers
        document.querySelectorAll('.btn-play').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const trackId = e.target.closest('.track-card').dataset.trackId;
                this.playTrack(trackId);
            });
        });
    }
    
    async playTrack(trackId) {
        try {
            const track = await API.get(`/tracks/${trackId}`);
            this.currentTrack = track;
            this.audio.src = track.preview_url;
            this.audio.play();
            this.isPlaying = true;
        } catch (error) {
            Toast.error('Error', 'Failed to play track');
        }
    }
    
    pause() {
        this.audio.pause();
        this.isPlaying = false;
    }
    
    toggle() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.audio.play();
            this.isPlaying = true;
        }
    }
}

const audioPlayer = new AudioPlayer();
