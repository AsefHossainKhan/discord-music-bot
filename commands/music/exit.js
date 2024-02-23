const { SlashCommandBuilder } = require('@discordjs/builders')
const { useMainPlayer } = require('discord-player')

module.exports = {
  data: new SlashCommandBuilder().setName('exit').
    setDescription('Kick the bot from the channel.'),
  async execute(interaction) {
    const player = useMainPlayer()

    // Get the current queue
    const queue = player.nodes.get(interaction.guildId)

    if (!queue) {
      await interaction.reply('There are no songs in the queue')
      return
    }

    // Deletes all the songs from the queue and exits the channel
    queue.delete()

    await interaction.reply('Why you do this to me?')
  },
}