import mido

class Bridge:
    """
    MIDI bridge for sending gestures to Ableton via loopMIDI.
    - Auto-selects a port that starts with "Shaka" if none provided.
    - send(action, value): Note On for discrete actions
    - send_cc_named(cc_name, value01): CC by symbolic name (0..1 -> 0..127)
    - send_cc(cc_number, value01): CC by number (compat)
    """
    def __init__(self, midi_port: str = None):
        self.outport = None
        self.port_name = None

        try:
            if midi_port:
                self.outport = mido.open_output(midi_port)
                self.port_name = midi_port
            else:
                port = next((p for p in mido.get_output_names() if p.lower().startswith("shaka")), None)
                if not port:
                    raise IOError("No MIDI port starting with 'Shaka' found. Create one in loopMIDI (e.g., 'Shaka 1').")
                self.outport = mido.open_output(port)
                self.port_name = port
            print(f"[Bridge] Connected to MIDI port: {self.port_name}")
        except Exception as e:
            print(f"[Bridge] MIDI port error: {e}")
            self.outport = None

        # -------- Deck-specific notes --------
        # Left hand = Deck A (Track 1)
        # Right hand = Deck B (Track 2)
        self.note_map = {
            # Deck A (Left Hand)
            "PLAY_A": 70, "STOP_A": 71, "REVERB_TOGGLE_A": 72, "FILTER_TOGGLE_A": 73,
            "SCRUB_A": 74,

            # Deck B (Right Hand)
            "PLAY_B": 80, "STOP_B": 81, "REVERB_TOGGLE_B": 82, "FILTER_TOGGLE_B": 83,
            "SCRUB_B": 84,
        }

        # -------- Deck-specific CCs --------
        self.cc_map = {
            "VOL_A": 7,    # Volume control for Track 1
            "VOL_B": 17,   # Volume control for Track 2
            "XFADE": 1     # Crossfader (optional)
        }

        self._last_cc = {}  

    def send(self, action: str, value: float = 1.0):
        """Send Note On for discrete actions (PLAY/STOP/TOGGLE)."""
        if not self.outport:
            print("[Bridge] No MIDI output port. Is loopMIDI running?")
            return

        note = self.note_map.get(action.upper())
        if note is None:
            print(f"[Bridge] Unknown action '{action}'.")
            return

        vel = int(max(0.0, min(1.0, value)) * 127)
        msg = mido.Message("note_on", note=note, velocity=vel)
        self.outport.send(msg)
        print(f"[MIDI NOTE] {action.upper()} → note {note}, velocity {vel}")

    def send_cc_named(self, cc_name: str, value01: float):
        """Send CC by symbolic name (e.g., 'VOL_A', 'VOL_B', 'XFADE')."""
        if not self.outport:
            print("[Bridge] No MIDI output port. Is loopMIDI running?")
            return
        cc_num = self.cc_map.get(cc_name)
        if cc_num is None:
            print(f"[Bridge] Unknown CC '{cc_name}'.")
            return
        v = int(max(0.0, min(1.0, value01)) * 127)
        # --- de-dup: don't send if same value as last time for this CC ---
        if self._last_cc.get(cc_num) == v:  
            return                           
        self._last_cc[cc_num] = v            
        self.outport.send(mido.Message("control_change", control=cc_num, value=v))
        print(f"[MIDI CC] {cc_name} (CC#{cc_num}) = {v}")

    def send_cc(self, cc_number: int, value01: float):
        """Send CC by number directly (kept for compatibility)."""
        if not self.outport:
            print("[Bridge] No MIDI output port. Is loopMIDI running?")
            return
        v = int(max(0.0, min(1.0, value01)) * 127)
        # --- de-dup ---
        if self._last_cc.get(cc_number) == v:  
            return                              
        self._last_cc[cc_number] = v           
        self.outport.send(mido.Message("control_change", control=cc_number, value=v))
        print(f"[MIDI CC] CC#{cc_number} = {v}")

    def close(self):
        if self.outport:
            self.outport.close()
            print("[Bridge] MIDI port closed.")
