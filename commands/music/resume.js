const { SlashCommandBuilder } = require('@discordjs/builders')
const { useMasterPlayer } = require('discord-player')

module.exports = {
  data: new SlashCommandBuilder().setName('resume').
    setDescription('Resumes the current song'),
  async execute (interaction) {
    const player = useMasterPlayer()
    // Get the queue for the server
    const queue = player.nodes.get(interaction.guildId)

    // Check if the queue is empty
    if (!queue) {
      await interaction.reply('No songs in the queue')
      return
    }

    // Resume the current song
    queue.node.resume()

    await interaction.reply('Player has been resumed.')
  },
}
