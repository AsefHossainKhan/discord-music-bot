import { SlashCommandBuilder } from "@discordjs/builders";
import { useMainPlayer } from "discord-player";

const Pause = {
  data: new SlashCommandBuilder()
    .setName("pause")
    .setDescription("Pauses the current song"),
  async execute(interaction) {
    const player = useMainPlayer();

    // Get the queue for the server
    const queue = player.nodes.get(interaction.guildId);

    // Check if the queue is empty
    if (!queue) {
      await interaction.reply("There are no songs in the queue");
      return;
    }

    // Pauses the current song
    queue.node.pause();

    await interaction.reply("Player has been paused.");
  },
};

export default Pause;
