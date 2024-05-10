import { SlashCommandBuilder } from "@discordjs/builders";
import { EmbedBuilder } from "discord.js";
import { Track, useMainPlayer } from "discord-player";

const Skip = {
  data: new SlashCommandBuilder()
    .setName("skip")
    .setDescription("Skips the current song"),

  async execute(interaction) {
    const player = useMainPlayer();

    // Get the queue for the server
    const queue = player.nodes.get(interaction.guildId);

    // If there is no queue, return
    if (!queue) {
      await interaction.reply("There are no songs in the queue");
      return;
    }

    const currentSong: Track = queue.currentTrack as Track;

    // Skip the current song
    queue.node.skip();

    // Return an embed to the user saying the song has been skipped
    await interaction.reply({
      embeds: [
        new EmbedBuilder()
          .setDescription(`${currentSong.title} has been skipped!`)
          .setThumbnail(currentSong.thumbnail),
      ],
    });
  },
};

export default Skip;
